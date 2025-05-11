import cv2
import pytesseract
import platform
from PIL import Image
import os
import re


if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def preprocess_image_for_ocr(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale_percent = 200
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LINEAR)
    thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 9)
    return thresh

def extract_text_from_image(image_path: str) -> str:
    try:
        processed_image = preprocess_image_for_ocr(image_path)
        raw_text = pytesseract.image_to_string(processed_image)
        utf8_text = raw_text.encode('utf-8', errors='ignore').decode('utf-8')
        return utf8_text.strip()
    except Exception as e:
        print("[ERROR] OCR failed:", e)
        return ""

def extract_address_from_text(text: str) -> str:
    match = re.search(r'\d{3,5}\s+[A-Z][a-zA-Z]*\s+(University|Main|Park|Cherry|6th|1st|2nd|Street|Avenue|Blvd)[^\n,]*', text)
    if match:
        return match.group(0).strip()
    return None

def extract_building_info(text: str):
    lines = text.splitlines()
    building_name = ""
    building_number = ""

    # Try extracting building number from any line
    for line in lines:
        if "building number" in line.lower():
            match = re.search(r"\d{1,4}", line)
            if match:
                building_number = match.group().strip()
    
    # Try extracting building name: Look for a line containing keywords like 'Main Library' or near known address
    for i, line in enumerate(lines):
        if re.search(r"\d{3,5}\s+E University Blvd", line):
            # look 2 lines above in case of spacing
            if i >= 2 and len(lines[i-2].strip()) > 3:
                building_name = lines[i-2].strip()
            elif i >= 1 and len(lines[i-1].strip()) > 3:
                building_name = lines[i-1].strip()
            else:
                building_name = "Unknown"

    return building_name.strip(), building_number.strip()

