#!/bin/bash

# Update package list and install Tesseract
apt-get update
apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-tha

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*
