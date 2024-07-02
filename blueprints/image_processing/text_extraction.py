from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import pytesseract
import re

# Initialize Flask Blueprint
text_extraction_bp = Blueprint("text_extraction", __name__)

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'

# Define regex patterns for extracting specific fields
name_pattern = re.compile(r'[A-Z]+, [A-Z]+ [A-Z]+')
license_pattern = re.compile(r'[A-Z]\d{2}-\d{2}-\d{6}')
expiration_pattern = re.compile(r'(?:202[4-9]|20[3-9]\d|2[1-9]\d{2}|[3-9]\d{3})/\d{2}/\d{2}')
agency_code_pattern = re.compile(r'\b[A-Z0-9]{3}\b')
birthday_pattern = re.compile(r'(19|20)\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])')

# Custom Tesseract configuration
custom_config = r'--oem 3 --psm 6'

# Function to process image and extract text
@text_extraction_bp.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Check if 'image' is present in request files
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"})

        # Read image file from request
        image_data = request.files['image'].read()

        # Convert image bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Decode numpy array into an image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Dilation on the green channel
        dilated_img = cv2.dilate(image[:, :, 1], np.ones((7, 7), np.uint8))

        # Median blur to get the background image
        bg_img = cv2.medianBlur(dilated_img, 21)

        # Absolute difference to preserve edges
        diff_img = 255 - cv2.absdiff(image[:, :, 1], bg_img)

        # Normalizing between 0 to 255
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        # Thresholding
        th = cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Perform OCR on the thresholded image with custom configuration
        extracted_text = pytesseract.image_to_string(th, config=custom_config)

        # Extract specific fields using regex patterns
        name = None
        license_number = None
        expiration_date = None
        agency_code = None
        birthday = None
        

        for line in extracted_text.split('\n'):
            line = line.strip()
            if name is None:
                name_match = name_pattern.search(line)
                if name_match:
                    name = name_match.group()
            if license_number is None:
                license_match = license_pattern.search(line)
                if license_match:
                    license_number = license_match.group()
            if expiration_date is None:
                expiration_match = expiration_pattern.search(line)
                if expiration_match:
                    expiration_date = expiration_match.group()
            if birthday is None:
                birthday_match = birthday_pattern.search(line)
                if birthday_match:
                    birthday = birthday_match.group()

        # Prepare response JSON with extracted data
        response_data = {
            "Name": name,
            "License Number": license_number,
            "Expiration Date": expiration_date,
            "Birthday": birthday
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"})

