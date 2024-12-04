import os
import re
import time
import fitz
from google.cloud import vision


class OCRDocumentLoader:
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path
        self.extracted_text_path = "extracted.txt"

        self.vision_client = vision.ImageAnnotatorClient(
            client_options={"api_key": os.environ.get("")}
        )

    def _detect_text(self, image_content):
        """Detects text in an image using Google Vision API."""
        image = vision.Image(content=image_content)
        start_time = time.time()
        response = self.vision_client.text_detection(image=image)
        end_time = time.time()
        texts = response.text_annotations

        if response.error.message:
            raise Exception(
                "{}/nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message
                )
            )

        if texts:
            return texts[0].description, end_time - start_time, texts[1:]
        else:
            return None, end_time - start_time, None

    def _convert_pdf_to_images(self):
        """Converts each page of the PDF to an image."""
        document = fitz.open(self.file_path)
        images = []
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            images.append(image_bytes)
        return images

    def process_file(self):
        images = self._convert_pdf_to_images()
        extracted_text = ""
        detection_time = 0
        all_text_annotations = []

        for image in images:
            text, time_taken, annotations = self._detect_text(image)
            if text:
                extracted_text += remove_byte_b5(text) + "/n"
                if annotations:
                    all_text_annotations.extend(annotations)
            detection_time += time_taken

        with open(self.extracted_text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)


def remove_byte_b5(text: str) -> str:
    text = re.sub(r"⚫", "", text)
    return text
