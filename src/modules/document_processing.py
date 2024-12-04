import base64
import logging
import os
from pathlib import Path
import re
from typing import Dict, Union, Optional
from PIL import Image
import pdf2image
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import requests
import backoff
import json
from dataclasses import dataclass
from enum import Enum

from openai import OpenAI
import google.generativeai as genai

from modules.site_data_processing import LandDataProcessor
from modules.logging import setup_logger
from utils.sample_data import sample_prompt_result

client = OpenAI()

MAX_RETRIES = 1

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.FileHandler("document_processor.log"), logging.StreamHandler()],
# )
# logger = logging.getLogger(__name__)

logger = setup_logger(name=__name__, log_dir="logs", level=logging.DEBUG)


class DocumentType(Enum):
    PDF = "pdf"
    IMAGE = "image"


@dataclass
class ProcessingResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class DocumentProcessor:
    def __init__(self, llm_api_key: str, max_retries: int = MAX_RETRIES):
        self.llm_api_key = llm_api_key
        self.max_retries = max_retries
        self.retry_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=3)

    def process_document(
        self,
        file_path: Union[str, Path],
        original_file_path: Union[str, Path],
        model_type="GEMINI",
    ) -> ProcessingResult:
        """Main entry point for document processing."""
        try:
            file_path = Path(file_path)
            logger.info(f"Starting processing of {file_path}")

            # Determine document type
            original_file_path = Path(original_file_path)
            doc_type = self._get_document_type(original_file_path)

            # Convert to image if PDF
            if doc_type == DocumentType.PDF:
                image = self._convert_pdf_to_image(file_path)
            else:
                image = self._load_image(file_path)

            # Process image
            return self._process_image(image, model_type)

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return ProcessingResult(success=False, error=str(e))

    @staticmethod
    def _get_document_type(file_path: Path) -> DocumentType:
        """Determine the type of document based on file extension."""
        if file_path.suffix.lower() == ".pdf":
            return DocumentType.PDF
        return DocumentType.IMAGE

    @backoff.on_exception(backoff.expo, Exception, max_tries=MAX_RETRIES)
    def _convert_pdf_to_image(self, file_path: Path) -> Image.Image:
        """Convert PDF to image with retry mechanism."""
        logger.info(f"Converting PDF to image: {file_path}")
        try:
            images = pdf2image.convert_from_path(file_path)
            return images[-1]  # Return first page
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise

    @staticmethod
    def _load_image(file_path: Path) -> Image.Image:
        """Load image file with basic validation."""
        try:
            image = Image.open(file_path)
            return image
        except Exception as e:
            logger.error(f"Image loading failed: {str(e)}")
            raise

    def _process_image(self, image: Image.Image, model_type: str) -> ProcessingResult:
        """Process image through LLM with retry mechanism."""
        retry_count = 0

        while retry_count < self.max_retries:
            try:
                # Prepare image for LLM
                processed_image = self._preprocess_image(image)
                logger.info("Image processing complete")

                # Send to LLM for extraction
                logger.info("LLM Processing Started")
                result = self._send_to_llm(processed_image, model_type)
                logger.info("LLM Processing Completed")

                # process extracted data
                logger.info("Validation and Processing Started")
                result = result = JSONProcessor.extract_json_safely(
                    result
                )
                # print(result)
                # result = self._process_site_data(result)
                logger.info("Validation and Processing Completed")

                # # Validate result
                if result:  # self._validate_result(result):
                    logger.info("Document processed successfully")
                    return ProcessingResult(
                        success=True, data={"image": processed_image, "results": result}
                    )

                logger.warning("Invalid result received, retrying...")
                retry_count += 1

            except Exception as e:
                logger.error(f"Processing attempt {retry_count + 1} failed: {str(e)}")
                retry_count += 1
                time.sleep(2**retry_count)  # Exponential backoff

        return ProcessingResult(success=False, error="Max retries exceeded")

    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image before sending to LLM."""
        # Add image preprocessing steps here (resize, enhance, etc.)
        return image

    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=MAX_RETRIES
    )
    def _send_to_llm(self, image: Image.Image, model_type: str = "OPENAI") -> dict:
        """Send image to LLM for analysis."""

        prompt: str = """
                The provided document contains a sample site plan. 
                The objective is to extract and structure specific information accurately. 
                ### Target Data to Extract:
                1. **Landowners**: Names of the landowners. Look for text starting with **FOR:** on the land plan.
                2. **Plot Number**: The plot number of the site plan.
                3. **Date**: The date mentioned in the document, if specified.
                4. **Area**: The area of the site plan.
                5. **Metric**: Units of the area (e.g., hectares or acres).
                6. **Scale**: The scale of the plan.
                7. **Locality**: The locality information of the site.
                8. **District**: The district name.
                9. **Region**: The region name.
                10. **Other Location Details**: Any additional location-related details.
                11. **Surveyers Name**: The name of the surveyor.
                12. **Suryors Location**: Location of the surveyor.
                13. **Suryors Number**: The registration number of the surveyor.
                11. **Regional Number**: The regional number associated with the plan.
                12. **Reference Number**: The reference number of the document.
                13. **Site Plan Data**:
                    - **Plan Data** (if in tabular form): Extract values from headings like:
                    - `From`
                    - `X (N) Coords`
                    - `Y (E) Coords`
                    - `Bearing`
                    - `Distance`
                    - `To`
                    - **North-Eastern Coordinates**: These may be found around the site plan image, in formats like:
                    - Example: `1245500E`, `1246000E`, `400000N`, `400500N`
                    - Or as numbers without directional indicators: `1245500`, `1246000`, `400000`, `400500`
                    
                **Note!**
                For X and Y coords add another property called ref
                IF the ENDING OF FROM TEXT FROMAT IS LIKE  10/2021/1 ref is false
                IF the ENDING OF FROM TEXT FROMAT IS LIKE CORS 2023 3 OR  A001 19 1 ref is true
                This is neccesary for accuratly plotting
                

                ### Output Format:
                Return the extracted information in JSON format with the following structure:
                ```json
                {
                "owners": [],
                "plot_number": "",
                "date": "",
                "area": "",
                "metric": "",
                "scale": "",
                "locality": "",
                "district": "",
                "region": "",
                "other_location_details": "",
                "surveyors_name: "",
                "surveyors_location: "",
                "surveyors_reg_number": "",
                "regional_number": "",
                "reference_number": "",
                "site_plan_data": {
                    "plan_data": {
                    "from": [],
                    "x_coords": [],
                    "y_coords": [],
                    "bearing": [],
                    "distance": [],
                    "to": []
                    },
                    "north_easterns": {
                    "norths": [],
                    "easterns": []
                    }
                }
                }
                ```
                ### Instructions:
                - Carefully analyze the document and execute the following instructions systematically.
                - If a field is not available in the document, leave it empty in the JSON output.
                - Pay special attention to coordinates and data tables. Ensure values align with their respective fields.
                - For **site plan data**, prioritize structured table data if available. Use surrounding context for coordinate extraction when no table is present.
                """

        if model_type == "GEMINI":
            response = self._gemini_model(image, prompt)
        else:
            response = self._openai_model(image, prompt)
        return response

    @staticmethod
    def _openai_model(image: Image.Image, prompt: str) -> Union[str, any]:

        # Convert image to bytes
        def encode_image():
            import io

            try:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="png")
                img_byte_arr = img_byte_arr.getvalue()
            except Exception as e:
                logger.info(f"Image Conversion to Bytes Failed: {str(e)}")
                raise e
            else:
                return encode_base_64_image(img_byte_arr)

        def encode_base_64_image(image_bytes):
            return base64.b64encode(image_bytes).decode("utf-8")

        try:
            image_data = encode_image()
            logger.info("OPENAI CALL!")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                ],
            )

            return response.choices[0].message.content

            return sample_prompt_result
        except Exception as e:
            logger.info(f"OPENAI Failed to Extract Site Plan Data: {str(e)}")
            raise e

    @staticmethod
    def _gemini_model(image: Image.Image, prompt: str) -> Union[str, any]:
        try:
            logger.info("GEMINI CALL!")
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
            response = model.generate_content([prompt, image]).to_dict()
            try:
                return response["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                return response
            return sample_prompt_result
        except Exception as e:
            logger.info(f"GEMINI Failed to Extract Site Plan Data: {str(e)}")
            raise e

    @staticmethod
    def _validate_result(result: dict) -> bool:
        """Validate LLM response."""
        required_fields = ["text", "confidence"]
        return all(field in result for field in required_fields)

    @staticmethod
    def _extract_json(text: str) -> dict:
        import re

        output_dict = {}

        if text:
            try:
                # Regex pattern to remove ```json and ```
                cleaned_text = re.sub(r"```json|```", "", text).strip()
                clean_json = json.dumps(cleaned_text)
                output_dict = json.loads(clean_json)
            except Exception:
                try:
                    output_dict = json.loads(text.strip())
                except Exception:
                    try:
                        # Regex pattern to extract JSON
                        json_pattern = r"{.*?}"
                        # Extract JSON using regex
                        json_match = re.search(json_pattern, text, re.DOTALL)
                        if json_match:
                            json_data = json_match.group(0)  # Get the matched JSON
                            clean_json = json.dumps(json_data)
                            output_dict = json.loads(clean_json)
                        else:
                            return None
                    except Exception:
                        return None

            if not isinstance(output_dict, dict):
                output_dict = json.loads(output_dict)
            return output_dict

    @staticmethod
    def _process_site_data(site_data) -> dict:
        try:
            processor = LandDataProcessor()
            results = processor.process_land_data(site_data)
            return results
        except Exception as e:
            logger.error(f"Failed to Process Site Data: {str(e)}")
            return None


class JSONExtractionError(Exception):
    """
    Custom exception for JSON extraction errors with detailed error information.

    Attributes:
        message (str): Error message
        error_type (str): Type of error encountered
        error_location (str): Where in the extraction process the error occurred
        original_error (Exception, optional): The original exception that caused this error
        input_data (str, optional): Snippet of the problematic input data
    """

    def __init__(
        self,
        message: str,
        error_type: str = "Unknown",
        error_location: str = "Unknown",
        original_error: Exception = None,
        input_data: str = None,
    ):
        self.message = message
        self.error_type = error_type
        self.error_location = error_location
        self.original_error = original_error
        self.input_data = (
            input_data[:100] if input_data else None
        )  # Limit input data length

        # Build detailed error message
        detailed_message = f"""
                JSON Extraction Error:
                - Message: {self.message}
                - Error Type: {self.error_type}
                - Location: {self.error_location}
                - Original Error: {str(self.original_error) if self.original_error else 'None'}
                - Input Data Preview: {self.input_data + '...' if self.input_data else 'None'}
                """
        super().__init__(detailed_message)

    @classmethod
    def from_parsing_error(
        cls, error: Exception, input_data: str = None
    ) -> "JSONExtractionError":
        """
        Create an extraction error from a JSON parsing error.

        Args:
            error (Exception): The original parsing error
            input_data (str, optional): The input data that caused the error

        Returns:
            JSONExtractionError: New instance with parsing error details
        """
        return cls(
            message="Failed to parse JSON data",
            error_type="ParseError",
            error_location="JSON Parser",
            original_error=error,
            input_data=input_data,
        )

    @classmethod
    def from_validation_error(
        cls, message: str, input_data: str = None
    ) -> "JSONExtractionError":
        """
        Create an extraction error from a validation failure.

        Args:
            message (str): Description of the validation failure
            input_data (str, optional): The input data that failed validation

        Returns:
            JSONExtractionError: New instance with validation error details
        """
        return cls(
            message=message,
            error_type="ValidationError",
            error_location="Data Validator",
            input_data=input_data,
        )

    @classmethod
    def from_extraction_failure(
        cls, method: str, error: Exception = None, input_data: str = None
    ) -> "JSONExtractionError":
        """
        Create an error for when extraction methods fail.

        Args:
            method (str): The extraction method that failed
            error (Exception, optional): The original error if any
            input_data (str, optional): The input data that caused the failure

        Returns:
            JSONExtractionError: New instance with extraction failure details
        """
        return cls(
            message=f"Failed to extract JSON using {method}",
            error_type="ExtractionError",
            error_location=method,
            original_error=error,
            input_data=input_data,
        )

    def get_error_dict(self) -> dict:
        """
        Get error information as a dictionary.

        Returns:
            dict: Error information in dictionary format
        """
        return {
            "message": self.message,
            "error_type": self.error_type,
            "location": self.error_location,
            "original_error": str(self.original_error) if self.original_error else None,
            "input_preview": self.input_data,
        }

    def log_error(self, logger) -> None:
        """
        Log the error using the provided logger.

        Args:
            logger: Logger instance to use for logging
        """
        logger.error(f"JSON Extraction Error: {self.message}")
        logger.debug(f"Error Type: {self.error_type}")
        logger.debug(f"Location: {self.error_location}")
        if self.original_error:
            logger.debug(f"Original Error: {str(self.original_error)}")
        if self.input_data:
            logger.debug(f"Input Preview: {self.input_data}")


class JSONProcessor:
    @staticmethod
    def _extract_json(text: str) -> Optional[Dict]:
        """
        Extract and parse JSON from text string with enhanced error handling and logging.

        Args:
            text (str): Input text containing JSON data

        Returns:
            Optional[Dict]: Parsed JSON dictionary or None if extraction fails

        Raises:
            JSONExtractionError: If JSON extraction fails after all attempts
        """
        logger.debug("Starting JSON extraction from text")

        if not text:
            logger.warning("Empty text provided for JSON extraction")
            return None

        # Store the original text length for logging
        original_length = len(text)
        logger.debug(f"Input text length: {original_length} characters")

        def attempt_json_load(json_str: str, context: str) -> Optional[Dict]:
            """Helper function to attempt JSON loading with consistent error handling."""
            try:
                result = json.loads(json_str)
                if not isinstance(result, dict):
                    logger.debug(
                        f"{context}: Result is not a dictionary, attempting conversion"
                    )
                    # If result is a string containing JSON, try parsing it
                    if isinstance(result, str):
                        result = json.loads(result)
                if isinstance(result, dict):
                    logger.debug(f"Successfully parsed JSON in {context}")
                    return result
                else:
                    logger.debug(
                        f"{context}: Result is not a dictionary after conversion"
                    )
                    return None
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parsing failed in {context}: {str(e)}")
                return None
            except Exception as e:
                logger.debug(f"Unexpected error in {context}: {str(e)}")
                return None

        # Method 1: Direct JSON parsing after cleaning markdown
        try:
            logger.debug("Attempting Method 1: Markdown cleanup and direct parsing")
            cleaned_text = re.sub(r"```json|```", "", text).strip()
            logger.debug(f"Cleaned text length: {len(cleaned_text)} characters")
            
            print(cleaned_text)

            clean_json = json.dumps(cleaned_text)
            result = attempt_json_load(clean_json, "Method 1")
            if result:
                return result
        except Exception as e:
            logger.debug(f"Method 1 failed: {str(e)}")

        # Method 2: Direct JSON parsing of original text
        try:
            logger.debug("Attempting Method 2: Direct parsing of original text")
            result = attempt_json_load(text.strip(), "Method 2")
            if result:
                return result
        except Exception as e:
            logger.debug(f"Method 2 failed: {str(e)}")

        # Method 3: Regex extraction and parsing
        try:
            logger.debug("Attempting Method 3: Regex extraction")
            json_pattern = r"{.*?}"
            json_match = re.search(json_pattern, text, re.DOTALL)

            if json_match:
                json_data = json_match.group(0)
                logger.debug(f"Found JSON match of length: {len(json_data)} characters")

                clean_json = json.dumps(json_data)
                result = attempt_json_load(clean_json, "Method 3")
                if result:
                    return result
            else:
                logger.debug("No JSON pattern match found")
        except Exception as e:
            logger.debug(f"Method 3 failed: {str(e)}")

        # If all methods fail
        logger.error("All JSON extraction methods failed")
        error_msg = (
            f"Failed to extract valid JSON from text of length {original_length}"
        )
        logger.error(error_msg)
        raise JSONExtractionError(error_msg)

    @classmethod
    def extract_json_safely(cls, text: str) -> Optional[Dict]:
        """
        Public wrapper method for JSON extraction with high-level error handling.

        Args:
            text (str): Input text containing JSON data

        Returns:
            Optional[Dict]: Parsed JSON dictionary or None if extraction fails
        """
        try:
            return cls._extract_json(text)
        except JSONExtractionError as e:
            logger.error(f"JSON extraction error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during JSON extraction: {str(e)}")
            return None
