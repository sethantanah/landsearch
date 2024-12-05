import io
import os
import re
import time
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Tuple, List, Optional, Any
from google.cloud import vision

from modules.logging import setup_logger


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    def __init__(self, message: str, error_type: str = "Unknown", original_error: Exception = None):
        self.message = message
        self.error_type = error_type
        self.original_error = original_error
        super().__init__(self.message)

class OCRDocumentLoader:
    """Document loader that performs OCR using Google Vision API."""

    def __init__(self, image: Any) -> None:
        """
        Initialize the OCR document loader.

        Args:
            image: The image to process

        Raises:
            OCRError: If initialization fails
        """
        self.logger = setup_logger(name=__name__, log_dir="logs", level=logging.DEBUG)
        self.logger.info("Initializing OCR Document Loader")
        
        self.image = image
        self.extracted_text_path = "extracted.txt"

        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise OCRError("Google API key not found in environment variables", "ConfigError")
            
            self.vision_client = vision.ImageAnnotatorClient(
                client_options={"api_key": api_key}
            )
            self.logger.info("Successfully initialized Vision API client")
        
        except Exception as e:
            error_msg = "Failed to initialize Vision API client"
            self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise OCRError(error_msg, "InitializationError", e)

    def _detect_text(self, image_content: bytes) -> Tuple[Optional[str], float, Optional[List]]:
        """
        Detect text in an image using Google Vision API.

        Args:
            image_content: The image content in bytes

        Returns:
            Tuple containing extracted text, processing time, and text annotations

        Raises:
            OCRError: If text detection fails
        """
        self.logger.debug("Starting text detection")
        try:
            image = vision.Image(content=image_content)
            start_time = time.time()
            response = self.vision_client.text_detection(image=image)
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.logger.debug(f"Text detection completed in {processing_time:.2f} seconds")

            if response.error.message:
                raise OCRError(
                    f"Google Vision API error: {response.error.message}",
                    "APIError"
                )

            texts = response.text_annotations
            if texts:
                self.logger.info(f"Successfully extracted text ({len(texts)} annotations)")
                return texts[0].description, processing_time, texts[1:]
            else:
                self.logger.warning("No text detected in image")
                return None, processing_time, None

        except Exception as e:
            error_msg = "Google Vision API request failed"
            self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise OCRError(error_msg, "APIError", e)
        
        except Exception as e:
            error_msg = "Unexpected error during text detection"
            self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise OCRError(error_msg, "TextDetectionError", e)

    def _convert_pdf_to_images(self) -> bytes:
        """
        Convert PDF page to image.

        Returns:
            Image bytes

        Raises:
            OCRError: If conversion fails
        """
        self.logger.debug("Converting PDF to image")
        try:
            img_byte_arr = io.BytesIO()
            self.image.save(img_byte_arr, format="png")
            image_bytes = img_byte_arr.getvalue()
            self.logger.debug("Successfully converted PDF to image")
            return image_bytes

        except Exception as e:
            error_msg = "Failed to convert PDF to image"
            self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise OCRError(error_msg, "ConversionError", e)

    def process_file(self) -> Tuple[str, float, List]:
        """
        Process the file and extract text.

        Returns:
            Tuple containing extracted text, total processing time, and annotations

        Raises:
            OCRError: If processing fails
        """
        self.logger.info("Starting file processing")
        try:
            images = [self._convert_pdf_to_images()]
            extracted_text = ""
            detection_time = 0
            all_text_annotations = []

            for i, image in enumerate(images, 1):
                self.logger.debug(f"Processing image {i}/{len(images)}")
                text, time_taken, annotations = self._detect_text(image)
                
                if text:
                    cleaned_text = remove_byte_b5(text)
                    extracted_text += cleaned_text + "\n"
                    if annotations:
                        all_text_annotations.extend(annotations)
                detection_time += time_taken

            # Save extracted text
            try:
                # with open(self.extracted_text_path, "w", encoding="utf-8") as f:
                #     f.write(extracted_text)
                self.logger.info(f"Successfully saved extracted text to {self.extracted_text_path}")
            except Exception as e:
                error_msg = f"Failed to save extracted text to {self.extracted_text_path}"
                self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
                raise OCRError(error_msg, "FileWriteError", e)

            self.logger.info(f"File processing completed in {detection_time:.2f} seconds")
            return extracted_text

        except OCRError:
            raise
        except Exception as e:
            error_msg = "Unexpected error during file processing"
            self.logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise OCRError(error_msg, "ProcessingError", e)

def remove_byte_b5(text: str) -> str:
    """
    Remove specific characters from text.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    return re.sub(r"⚫", "", text)