 Urdu Text Recognition from Images and PDFs

This project is an Urdu OCR (Optical Character Recognition) system. It can read printed Urdu text from image files (like JPG, PNG) and PDFs, and convert it into editable Urdu text using only free and open-source tools.

What This Project Does

- Takes image or PDF files as input
- Finds and reads any printed Urdu text
- Shows the output as clean Urdu text in Unicode format
- Can be used for scanned pages, posters, books, etc.

 Tools and Libraries Used

- Python
- Tesseract OCR (free OCR engine)
- pdf2image (for converting PDFs to images)
- OpenCV and Pillow (for image processing)
- Streamlit (for making a simple web app)

How to Run This Project

Step 1: Install Python and Git

Make sure Python is installed on your computer. You also need Git to clone the project.

Step 2: Download the Project


git clone https://github.com/yourusername/urdu-ocr-ai-task.git
cd urdu-ocr-ai-task

Step 3: Set Up the Project

python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
Step 4: Download Urdu Language File
Download urd.traineddata from:
https://github.com/tesseract-ocr/tessdata/blob/main/urd.traineddata

Place it in your Tesseract OCR tessdata folder.

Example (on Windows):
C:\Program Files\Tesseract-OCR\tessdata\

Step 5: Run the App

streamlit run app.py
Then open the link shown in the terminal in your browser to use the tool.

How It Works
If you upload a PDF, it is first converted into images.

All images (from PDF or uploaded directly) are cleaned using basic image processing.

Tesseract OCR then tries to detect and extract any Urdu text.

The extracted text is displayed on screen.