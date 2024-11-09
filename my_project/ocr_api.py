from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pytesseract
from pdf2image import convert_from_path
import os
import re
import subprocess
import logging

app = Flask(__name__)
import pytesseract



# Enable CORS for all routes
CORS(app)

# Ensure Tesseract is specified if necessary


# Use the environment variable for Tesseract command
#print("Tesseract path:", pytesseract.pytesseract.tesseract_cmd)

pytesseract.pytesseract.tesseract_cmd = 'tesseract'  # You can try changing this path

# Or use the environment variable if set correctly
#pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD', 'tesseract')
#print("Tesseract path used:", pytesseract.pytesseract.tesseract_cmd)
#print(pytesseract.pytesseract.tesseract_cmd)  # To debug path

  # Adjust if needed
@app.route('/check-tesseract')
def check_tesseract():
    try:
        import pytesseract
        return jsonify({"tesseract_path": pytesseract.pytesseract.tesseract_cmd})
    except Exception as e:
        return jsonify({"error": str(e)})  



@app.route('/ocr_401', methods=['POST']) #เงินเดือน
def ocr_401():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Determine the file type
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    print(f"Processing file: {file.filename} with extension: {file_extension}")

    try:
        if file_extension == 'pdf':
            # Process as a PDF
            pdf_path = os.path.join('temp', file.filename)
            os.makedirs('temp', exist_ok=True)
            file.save(pdf_path)

            images = convert_from_path(pdf_path)
            extracted_data = []
            for img in images:
                text = pytesseract.image_to_string(img, lang='tha')
                structured_data = parse_extracted_text401(text)
                extracted_data.append(structured_data)

            os.remove(pdf_path)
            return jsonify({"extracted_texts": extracted_data}), 200

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # Process as an image
            img_path = os.path.join('temp', file.filename)
            os.makedirs('temp', exist_ok=True)
            file.save(img_path)

            # Perform OCR
            text = pytesseract.image_to_string(img_path, lang='tha')
            structured_data = parse_extracted_text401(text)

            os.remove(img_path)
            return jsonify({"extracted_texts": [structured_data]}), 200

        else:
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        print(f"Error processing the file: {e}")
        return jsonify({"error": str(e)}), 500

#ใบเงินเดือน  
def parse_extracted_text401(text):
    # Initialize a dictionary to hold the structured data
    data = {
        "employee": {},
        "salary_details": {
            "deductions": {}
        },
        "payment_date": ""
    }

    # Clean up the text to remove extra newlines and whitespace
    cleaned_text = " ".join(text.split())

    # Example regex patterns to extract the required information
    name_pattern = r"ชื่อ-สกุล\s+([^\s]+ [^\s]+)"  # Capture the name (two words)
    position_pattern = r"ตำแหน่ง\s+\|\s*([^\s]+)"  # Capture the position right after "ตำแหน่ง |"
    payment_date_pattern = r"วันที่จ่าย\s+([0-9]{1,2} [A-Za-z]{3}\.[0-9]{4})"  # Capture the payment date format
    salary_pattern = r"รายเดือน\s+([\d,]+)"
    phone_allowance_pattern = r"ค่าโทรศัพท์\s+([\d,]+)"
    total_income_pattern = r"ยอดรวม\s+([\d,]+)"
    social_security_pattern = r"ประกันสังคม\s+([\d,]+)"
    withholding_tax_pattern = r"ภาษีหัก ณที่จ่าย\s+([\d,]+)"
    net_income_pattern = r"เยอดสุทธิ\s+([\d,]+)"

    # Use regex to find matches in the cleaned text
    name_match = re.search(name_pattern, cleaned_text)
    if name_match:
        data["employee"]["name"] = name_match.group(1).strip()  # Use only the captured name

    position_match = re.search(position_pattern, cleaned_text)
    if position_match:
        data["employee"]["position"] = position_match.group(1).strip()  # Capture the position

    salary_match = re.search(salary_pattern, cleaned_text)
    if salary_match:
        data["salary_details"]["monthly_salary"] = int(salary_match.group(1).replace(',', '').strip())

    phone_allowance_match = re.search(phone_allowance_pattern, cleaned_text)
    if phone_allowance_match:
        data["salary_details"]["phone_allowance"] = int(phone_allowance_match.group(1).replace(',', '').strip())

    total_income_match = re.search(total_income_pattern, cleaned_text)
    if total_income_match:
        data["salary_details"]["total_income"] = int(total_income_match.group(1).replace(',', '').strip())

    # Initialize deductions if they weren't found in the text
    data["salary_details"]["deductions"] = {
        "social_security": 0,
        "withholding_tax": 0
    }

    social_security_match = re.search(social_security_pattern, cleaned_text)
    if social_security_match:
        data["salary_details"]["deductions"]["social_security"] = int(social_security_match.group(1).replace(',', '').strip())

    withholding_tax_match = re.search(withholding_tax_pattern, cleaned_text)
    if withholding_tax_match:
        data["salary_details"]["deductions"]["withholding_tax"] = int(withholding_tax_match.group(1).replace(',', '').strip())

    net_income_match = re.search(net_income_pattern, cleaned_text)
    if net_income_match:
        data["salary_details"]["net_income"] = int(net_income_match.group(1).replace(',', '').strip())

    payment_date_match = re.search(payment_date_pattern, cleaned_text)
    if payment_date_match:
        data["payment_date"] = payment_date_match.group(1).strip()

    return data


@app.route('/')
def home():
    return "Service is up and running!"

@app.route('/ocr_405', methods=['POST']) #donate
def ocr_405():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Determine the file type
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    print(f"Processing file: {file.filename} with extension: {file_extension}")

    try:
        os.makedirs('temp', exist_ok=True)
        
        raw_texts = []  # List to store raw OCR text
        
        if file_extension == 'pdf':
            # Process as a PDF
            pdf_path = os.path.join('temp', file.filename)
            file.save(pdf_path)

            images = convert_from_path(pdf_path)
            for img in images:
                # Perform OCR on each image
                text = pytesseract.image_to_string(img, lang='tha')
                raw_texts.append(text)  # Add raw text to the list

            # Clean up the PDF file after processing
            os.remove(pdf_path)

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # Process as an image
            img_path = os.path.join('temp', file.filename)
            file.save(img_path)

            # Perform OCR on the image
            text = pytesseract.image_to_string(img_path, lang='tha')
            raw_texts = [text]  # Store raw text in a list

            # Clean up the image file after processing
            os.remove(img_path)

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Parse the extracted text
        parsed_data = [parse_extracted_text405(text) for text in raw_texts]

        return jsonify({"donation_receipt": parsed_data}), 200

    except Exception as e:
        print(f"Error processing the file: {e}")
        return jsonify({"error": str(e)}), 500


def parse_extracted_text405(text): #donate 
    # Dictionary to hold extracted data in the desired structure
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


def parse_extracted_text_rented(text):
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
    recipient_name_pattern = r"ชือผู้รับบ\s*:\s*([^\n]+)"
    recipient_tax_id_pattern = r"เลขประจําตัวผู้เสียภาษี\s*:\s*([\d]+)"
    payer_name_pattern = r"ได้รับเงินจาก\s*:\s*([^\n]+)"
    property_type_pattern = r"เพื่อชําระค่าเช่า\s*:\s*([^\n]+)"
    payment_method_pattern = r"ชําระเป็น\s*([^\n]+)"
    payment_date_pattern = r"วันที่จ่าย\s*([^\n]+)"
    period_date_pattern = r"ประจํางวด\s*([^\n]+)"
    rent_amount_pattern = r"ค่าเช่า\s*([\d,]+)"
    total_amount_pattern = r"ยอดรวม\s*([\d,]+)"

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
    