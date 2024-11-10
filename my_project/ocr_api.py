from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pytesseract
from pdf2image import convert_from_path

import os
import re
import subprocess
import logging
import io
from PIL import Image,UnidentifiedImageError
app = Flask(__name__)
import pytesseract



# Enable CORS for all routes
CORS(app)

# Ensure Tesseract is specified if necessary


# Use the environment variable for Tesseract command
#print("Tesseract path:", pytesseract.pytesseract.tesseract_cmd)

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # You can try changing this path

# Or use the environment variable if set correctly
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD', 'tesseract')
#print("Tesseract path used:", pytesseract.pytesseract.tesseract_cmd)
#print(pytesseract.pytesseract.tesseract_cmd)  # To debug path

  # Adjust if needed
#docker run -p 5001:5000 flask-ocr
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import os
import re
from flask import jsonify, request

@app.route('/ocr_405', methods=['POST'])
def ocr_405():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Determine the file type
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    print(f"Processing file: {file.filename} with extension: {file_extension}")

    try:
        os.makedirs('temp', exist_ok=True)

        raw_text = ""  # Variable to store raw OCR text
        
        if file_extension == 'pdf':
            # Process as a PDF
            pdf_path = os.path.join('temp', file.filename)
            file.save(pdf_path)

            images = convert_from_path(pdf_path)
            for img in images:
                # Perform OCR on each image
                text = pytesseract.image_to_string(img, lang='tha')
                raw_text += text + "\n"  # Add raw text to the result

            # Clean up the PDF file after processing
            os.remove(pdf_path)

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # Process as an image
            img_path = os.path.join('temp', file.filename)
            file.save(img_path)

            # Perform OCR on the image
            text = pytesseract.image_to_string(img_path, lang='tha')
            raw_text = text  # Store raw text in a variable

            # Clean up the image file after processing
            os.remove(img_path)

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        raw_text = clean_raw_text(raw_text)
        parsed_data = parse_extracted_text405(raw_text)

        # Return the parsed data as a JSON response
        return jsonify(parsed_data), 200

    except Exception as e:
        print(f"Error processing the file: {e}")
        return raw_text#jsonify({"error": str(e)}), 500

def parse_extracted_text405(text): #donate 
    # Dictionary to hold extracted data in the desired structure
    text = clean_raw_text(text)
    data = {
        "hospital_name": "",
        "reference_number": "",
        "address": {
            "street": "",
            "sub_district": "",
            "district": "",
            "city": "",
            "postal_code": ""
        },
        "date": "",
        "time": "",
        "donor": {
            "name": "",
            "tax_id": ""
        },
        "donation_details": {
            "purpose": "",
            "amount": 0.0,
            "currency": "บาท"
        }
    }

    # Example regex patterns for extracting information from the text
    hospital_name_pattern = r"(ภาสกรการุณเวช)"
    reference_number_pattern = r"หมายเลขอ้างอิง\s*[:：]?\s*(\d+)"
    address_pattern = {
        "street": r"เลขที่\s*[:：]?\s*([\d\s]+)",  # Extracting street
        "sub_district": r"แขวง\s*[:：]?\s*([^\n]+)",  # Extracting sub-district
        "district": r"เขต\s*[:：]?\s*([^\n]+)",  # Extracting district
        "city": r"จังหวัด\s*[:：]?\s*([^\n]+)",  # Extracting city
        "postal_code": r"รหัสไปรษณีย์\s*[:：]?\s*(\d+)"  # Extracting postal code
    }
    date_pattern = r"วันที่\s*[:：]?\s*([\d\s]+)"  # Extracting date
    time_pattern = r"เวลา\s*[:：]?\s*([\d\s]+)"  # Extracting time
    donor_name_pattern = r"ชื่อผู้บริจาค\s*[:：]?\s*([^\n]+)"  # Donor name pattern
    donor_tax_id_pattern = r"เลขประจําตัวผู้เสียภาษี\s*[:：]?\s*(\d+)"  # Donor tax ID pattern
    donation_purpose_pattern = r"บริจาค\s*เงิน\s*เพื่อ\s*([\s\S]+?)\s*จำนวนเงิน"  # Donation purpose pattern
    amount_pattern = r"จํานวนเงิน\s*[:：]?\s*([\d,]+(?:\.\d{2})?)\s*บาท"  # Adjusted to capture the amount

    # Apply regex to populate data dictionary
    data["hospital_name"] = extract_value(hospital_name_pattern, text)
    data["reference_number"] = extract_value(reference_number_pattern, text)

    # Extract address details
    for key, pattern in address_pattern.items():
        data["address"][key] = extract_value(pattern, text)

    data["date"] = extract_value(date_pattern, text)
    data["time"] = extract_value(time_pattern, text)
    
    # Extract donor details
    data["donor"]["name"] = extract_value(donor_name_pattern, text)
    data["donor"]["tax_id"] = extract_value(donor_tax_id_pattern, text)

    # Extract donation details
    data["donation_details"]["purpose"] = extract_value(donation_purpose_pattern, text)
    data["donation_details"]["amount"] = extract_float_value(amount_pattern, text)
    
    return data

def extract_value(pattern, text):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""

def extract_float_value(pattern, text):
    match = re.search(pattern, text)
    if match:
        amount_str = match.group(1).replace(",", "")  # Remove commas before converting to float
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    return 0.0


#401
@app.route('/ocr_401', methods=['POST']) #เงินเดือน
def ocr_401():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Determine the file type
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    print(f"Processing file: {file.filename} with extension: {file_extension}")

    try:
        os.makedirs('temp', exist_ok=True)

        raw_text = ""  # Variable to store raw OCR text
        
        if file_extension == 'pdf':
            # Process as a PDF
            pdf_path = os.path.join('temp', file.filename)
            file.save(pdf_path)

            images = convert_from_path(pdf_path)
            for img in images:
                # Perform OCR on each image
                text = pytesseract.image_to_string(img, lang='tha')
                raw_text += text + "\n"  # Add raw text to the result

            # Clean up the PDF file after processing
            os.remove(pdf_path)

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # Process as an image
            img_path = os.path.join('temp', file.filename)
            file.save(img_path)

            # Perform OCR on the image
            text = pytesseract.image_to_string(img_path, lang='tha')
            raw_text = clean_raw_text(text)  # Store raw text in a variable

            # Clean up the image file after processing
            os.remove(img_path)

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Parse the raw OCR text to extract specific information for rented receipt
        parsed_data = parse_extracted_text_salary_slip(clean_raw_text(raw_text))

        # Return the parsed data as a JSON response
        return jsonify(parsed_data), 200

    except Exception as e:
        print(f"Error processing the file: {e}")
        return jsonify({"error": str(e)}), 500

#ใบเงินเดือน  
def parse_extracted_text_salary_slip(text):
    text = clean_raw_text(text)  # Clean the text first

    data = {
        "address": {
            "city": "",
            "district": "",
            "postal_code": "",
            "street": "",
            "sub_district": ""
        },
        "date": "",
        "donation_details": {
            "amount": 0.0,
            "currency": "บาท",
            "purpose": ""
        },
        "donor": {
            "name": "",
            "tax_id": ""
        },
        "hospital_name": "",
        "reference_number": "",
        "time": "",
        "income_details": {
            "salary": 0.0,
            "phone_cost": 0.0,
            "total_income": 0.0,
            "total_deductions": 0.0,
            "net_income": 0.0
        }
    }

    # Regex patterns for extracting data
    tax_id_pattern = r"เลขประจําตัวผู้เสียภาษี:\s*(\d+)"
    employee_id_pattern = r"รหัสพนักงาน(\d+)"
    name_pattern = r"ชื่อ-สกุล([^\d]+)"
    salary_pattern = r"รายได้จํานวนเงิน([\d,]+)"
    phone_cost_pattern = r"ค่าโทรศัพท์([\d,]+)"
    total_income_pattern = r"ยอดรวม([\d,]+)"
    deductions_pattern = r"รายการหักจํานวนเงินประกันสังคม([\d,]+)"
    total_deductions_pattern = r"รายการหักจํานวนเงิน([\d,]+)"
    net_income_pattern = r"ยอดสุทธิ([\d,]+)"
    payment_date_pattern = r"วันที่จ่ย(\d{4}-\d{2}-\d{2})"
    period_date_pattern = r"ประจํางวด(\d{4}-\d{2})"
    city_pattern = r"แขวง([^\d]+)"
    district_pattern = r"เขต([^\d]+)"
    postal_code_pattern = r"(\d{5})"

    # Extract the data using regex
    data["donor"]["tax_id"] = re.search(tax_id_pattern, text).group(1) if re.search(tax_id_pattern, text) else ""
    data["donor"]["name"] = re.search(name_pattern, text).group(1).strip() if re.search(name_pattern, text) else ""
    data["income_details"]["salary"] = float(re.search(salary_pattern, text).group(1).replace(",", "")) if re.search(salary_pattern, text) else 0.0
    data["income_details"]["phone_cost"] = float(re.search(phone_cost_pattern, text).group(1).replace(",", "")) if re.search(phone_cost_pattern, text) else 0.0
    data["income_details"]["total_income"] = float(re.search(total_income_pattern, text).group(1).replace(",", "")) if re.search(total_income_pattern, text) else 0.0
    data["income_details"]["total_deductions"] = float(re.search(deductions_pattern, text).group(1).replace(",", "")) if re.search(deductions_pattern, text) else 0.0
    data["income_details"]["net_income"] = float(re.search(net_income_pattern, text).group(1).replace(",", "")) if re.search(net_income_pattern, text) else 0.0
    data["date"] = re.search(payment_date_pattern, text).group(1) if re.search(payment_date_pattern, text) else ""
    data["period_date"] = re.search(period_date_pattern, text).group(1) if re.search(period_date_pattern, text) else ""
    data["address"]["sub_district"] = re.search(city_pattern, text).group(1) if re.search(city_pattern, text) else ""
    data["address"]["district"] = re.search(district_pattern, text).group(1) if re.search(district_pattern, text) else ""
    data["address"]["postal_code"] = re.search(postal_code_pattern, text).group(1) if re.search(postal_code_pattern, text) else ""
    
    return data



#ใบลดหย่อนรับบริจาค
@app.route('/rented', methods=['POST'])
def rented():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Determine the file type
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    print(f"Processing file: {file.filename} with extension: {file_extension}")

    try:
        os.makedirs('temp', exist_ok=True)

        raw_text = ""  # Variable to store raw OCR text
        
        if file_extension == 'pdf':
            # Process as a PDF
            pdf_path = os.path.join('temp', file.filename)
            file.save(pdf_path)

            images = convert_from_path(pdf_path)
            for img in images:
                # Perform OCR on each image
                text = pytesseract.image_to_string(img, lang='tha')
                raw_text += text + "\n"  # Add raw text to the result

            # Clean up the PDF file after processing
            os.remove(pdf_path)

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # Process as an image
            img_path = os.path.join('temp', file.filename)
            file.save(img_path)

            # Perform OCR on the image
            text = pytesseract.image_to_string(img_path, lang='tha')
            raw_text = text  # Store raw text in a variable

            # Clean up the image file after processing
            os.remove(img_path)

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Parse the raw OCR text to extract specific information for rented receipt
        parsed_data = parse_extracted_text_rented(raw_text)

        # Return the parsed data as a JSON response
        return jsonify(parsed_data), 200

    except Exception as e:
        print(f"Error processing the file: {e}")
        return jsonify({"error": str(e)}), 500


def clean_raw_text(text):
    # Remove spaces between characters
    return re.sub(r'\s+', '', text)

def parse_extracted_text_rented(text):
    text = clean_raw_text(text)  # Clean the text first

    data = {
        "recipient_name": "",
        "recipient_tax_id": "",
        "payer_name": "",
        "property_type": "",
        "payment_method": "",
        "payment_date": "",
        "period_date": "",
        "income": {
            "rent": 0,
            "total": 0
        }
    }

    # Example regex patterns for rented receipt
    recipient_name_pattern = r"ชือผู้รับบ:([^:]+)"
    recipient_tax_id_pattern = r"เลขประจําตัวผู้เสียภาษี:([\d]+)"
    payer_name_pattern = r"ได้รับเงินจาก:([^:]+)"
    property_type_pattern = r"เพื่อชําระค่าเช่า:([^:]+)"
    payment_method_pattern = r"ชําระเป็น([^:]+)"
    payment_date_pattern = r"วันที่จ่าย([^:]+)"
    period_date_pattern = r"ประจํางวด([^:]+)"
    rent_amount_pattern = r"ค่าเช่า([\d,]+)"
    total_amount_pattern = r"ยอดรวม([\d,\.]+)"

    # Apply regex to populate data dictionary
    data["recipient_name"] = re.search(recipient_name_pattern, text).group(1).strip() if re.search(recipient_name_pattern, text) else ""
    data["recipient_tax_id"] = re.search(recipient_tax_id_pattern, text).group(1).strip() if re.search(recipient_tax_id_pattern, text) else ""
    data["payer_name"] = re.search(payer_name_pattern, text).group(1).strip() if re.search(payer_name_pattern, text) else ""
    data["property_type"] = re.search(property_type_pattern, text).group(1).strip() if re.search(property_type_pattern, text) else ""
    data["payment_method"] = re.search(payment_method_pattern, text).group(1).strip() if re.search(payment_method_pattern, text) else ""
    data["payment_date"] = re.search(payment_date_pattern, text).group(1).strip() if re.search(payment_date_pattern, text) else ""
    data["period_date"] = re.search(period_date_pattern, text).group(1).strip() if re.search(period_date_pattern, text) else ""
    data["income"]["rent"] = int(re.search(rent_amount_pattern, text).group(1).replace(",", "")) if re.search(rent_amount_pattern, text) else 0
    data["income"]["total"] = float(re.search(total_amount_pattern, text).group(1).replace(",", "")) if re.search(total_amount_pattern, text) else 0.0

    return data



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
# Enable debug mode to see detailed errors
    