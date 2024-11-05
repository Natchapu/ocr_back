import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import json
import os
import shutil
import shutil  # Add this import at the top

# Ensure Tesseract is specified if necessary
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Adjust if needed

# Function to perform OCR on an image
# Function to perform OCR on an image
def ocr_image(image_path):
    print(f"Attempting to process image: {image_path}")
    try:
        # Load the image using Pillow
        img = Image.open(image_path)
        print("Image loaded successfully.")

        # Perform OCR using pytesseract with Thai language
        text = pytesseract.image_to_string(img, lang='tha')  # Specify Thai language
        print("OCR performed successfully.")
        
        # Remove or comment out the print statement to avoid terminal output
        # print("Extracted Text:")
        # print(text)

        # Save the extracted text to a JSON file
        output_data = {
           # "image_path": image_path,
            #"extracted_text": text
        }
        save_to_json(output_data, image_path)
    except Exception as e:
        print(f"Error processing the image: {e}")

# Function to convert PDF to images and perform OCR


# Function to cleanup images after OCR
def cleanup_images(images):
    for image in images:
        try:
            os.remove(image)  # Remove each image file
            print(f"Removed image: {image}")
        except Exception as e:
            print(f"Error removing image {image}: {e}")

# In the ocr_pdf function, modify the processing loop:
def ocr_pdf(pdf_path):
    print(f"Attempting to process PDF: {pdf_path}")
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        print(f"Converted PDF to {len(images)} images.")

        image_paths = []  # Store image paths for cleanup
        for i, img in enumerate(images):
            # Save each page as an image
            img_path = f"page_{i + 1}.png"
            img.save(img_path, "PNG")
            print(f"Saved image: {img_path}")
            ocr_image(img_path)  # Process the image using OCR
            image_paths.append(img_path)  # Add to list for cleanup

        cleanup_images(image_paths)  # Clean up saved images
    except Exception as e:
        print(f"Error processing the PDF: {e}")


# Function to save extracted text to a JSON file
def save_to_json(data, image_path):
    # Create a directory for the output if it doesn't exist
    output_dir = "/Users/puhple14/pyocr/output"
    os.makedirs(output_dir, exist_ok=True)

    # Create a JSON filename based on the image path
    json_filename = os.path.join(output_dir, os.path.basename(image_path).replace('.jpg', '.json').replace('.png', '.json'))
    
    # Save JSON with UTF-8 encoding
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    
    print(f"Output saved to JSON file: {json_filename}")
    

if __name__ == "__main__":
    print("Starting OCR process...")
    
    # Use the provided path to the PDF file
    ocr_pdf('/Users/puhple14/Desktop/PIT90_030162.pdf')  # Ensure this is the correct path to your PDF

    print("OCR process completed.")
