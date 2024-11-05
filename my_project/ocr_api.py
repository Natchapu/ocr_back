from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pytesseract
from pdf2image import convert_from_path
import os
import re

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Ensure Tesseract is specified if necessary
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Adjust if needed

@app.route('/ocr_pdf', methods=['POST'])
def ocr_pdf():
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
                structured_data = parse_extracted_text(text)
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
            structured_data = parse_extracted_text(text)

            os.remove(img_path)
            return jsonify({"extracted_texts": [structured_data]}), 200

        else:
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        print(f"Error processing the file: {e}")
        return jsonify({"error": str(e)}), 500




def parse_extracted_text(text):
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




if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)  # Enable debug mode to see detailed errors
