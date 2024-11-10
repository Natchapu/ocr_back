FROM python:3.9-slim

# Install dependencies, including Tesseract and its dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create the necessary directories for tessdata
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata

# Copy the trained data file into the container (ensure the path matches where the file is located on your host system)
COPY my_project/tha.traineddata /usr/share/tesseract-ocr/5/tessdata/tha.traineddata

# Set the working directory to /app
WORKDIR /app

# Copy everything in my_project to /app/my_project
COPY my_project /app/my_project
COPY requirements.txt .

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the required port and start the application
EXPOSE 5000
CMD ["python", "my_project/ocr_api.py"]
