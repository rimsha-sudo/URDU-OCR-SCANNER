import pytesseract
from PIL import Image
import cv2
import os
import sys
import numpy as np
from difflib import SequenceMatcher
import re

def setup_tesseract():
    
    """Setup Tesseract path - tries multiple common locations"""
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract'
    ]
    
    # Checking if tesseract is in PATH
    try:
        pytesseract.get_tesseract_version()
        return True
    except:
        pass
    
    # Try to set path from common locations
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            try:
                pytesseract.get_tesseract_version()
                return True
            except:
                continue
    
    return False

def check_urdu_language():
    """Check if Urdu language pack is available"""
    try:
        # Try to get available languages
        languages = pytesseract.get_languages()
        return 'urd' in languages
    except:
        return False

def calculate_accuracy(extracted_text, reference_text):
    """
    Calculate OCR accuracy by comparing extracted text with reference text
    
    Args:
        extracted_text (str): Text extracted by OCR
        reference_text (str): Original/correct text
        
    Returns:
        dict: Dictionary containing accuracy metrics
    """
    try:
        # Clean and preprocessing
        def clean_text(text):
            # Remove extra whitespace and normalize
            text = re.sub(r'\s+', ' ', text.strip())
            # Removal of  punctuation for character-level comparison
            text = re.sub(r'[^\w\s]', '', text)
            return text.lower()
        
        clean_extracted = clean_text(extracted_text)
        clean_reference = clean_text(reference_text)
        
        if not clean_reference:
            return {
                'overall_accuracy': 0,
                'character_accuracy': 0,
                'word_accuracy': 0,
                'similarity_score': 0,
                'error_details': 'Reference text is empty'
            }
        
        # Calculate different accuracy metrics
        
        # 1. Overall similarity using SequenceMatcher
        similarity = SequenceMatcher(None, clean_extracted, clean_reference).ratio()
        
        # 2. Character-level accuracy
        char_accuracy = 0
        if clean_reference:
            char_matches = sum(1 for a, b in zip(clean_extracted, clean_reference) if a == b)
            char_accuracy = char_matches / max(len(clean_reference), len(clean_extracted))
        
        # 3. Word-level accuracy
        extracted_words = set(clean_extracted.split())
        reference_words = set(clean_reference.split())
        
        if reference_words:
            word_matches = len(extracted_words.intersection(reference_words))
            word_accuracy = word_matches / len(reference_words)
        else:
            word_accuracy = 0
        
        # 4. Overall accuracy (weighted average)
        overall_accuracy = (similarity * 0.4 + char_accuracy * 0.3 + word_accuracy * 0.3) * 100
        
        # 5. Error analysis
        errors = []
        if len(clean_extracted) != len(clean_reference):
            errors.append(f"Length mismatch: extracted={len(clean_extracted)}, reference={len(clean_reference)}")
        
        missing_words = reference_words - extracted_words
        extra_words = extracted_words - reference_words
        
        if missing_words:
            errors.append(f"Missing words: {', '.join(list(missing_words)[:5])}")
        if extra_words:
            errors.append(f"Extra words: {', '.join(list(extra_words)[:5])}")
        
        return {
            'overall_accuracy': round(overall_accuracy, 2),
            'character_accuracy': round(char_accuracy * 100, 2),
            'word_accuracy': round(word_accuracy * 100, 2),
            'similarity_score': round(similarity * 100, 2),
            'extracted_length': len(clean_extracted),
            'reference_length': len(clean_reference),
            'missing_words': list(missing_words),
            'extra_words': list(extra_words),
            'error_details': '; '.join(errors) if errors else 'No major errors detected'
        }
        
    except Exception as e:
        return {
            'overall_accuracy': 0,
            'character_accuracy': 0,
            'word_accuracy': 0,
            'similarity_score': 0,
            'error_details': f'Error calculating accuracy: {str(e)}'
        }

def extract_urdu_text(image_path):
    """
    Extract Urdu text from an image file
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text or error message
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return "Error: Image file not found"
        
        # Setup Tesseract
        if not setup_tesseract():
            return "Error: Tesseract OCR not found. Please install Tesseract OCR and add it to PATH"
        
        # Check Urdu language availability
        if not check_urdu_language():
            return "Error: Urdu language pack not found. Please install urd.traineddata"
        
        # Load and validate image
        image = cv2.imread(image_path)
        if image is None:
            return "Error: Could not load image file"
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Optional preprocessing: apply thresholding for better OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(thresh, lang='urd')
        
        if not text.strip():
            return "No text detected in the image"
        
        return text.strip()
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_urdu_text_from_pil_image(pil_image):
    """
    Extract Urdu text from a PIL Image object
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        str: Extracted text or error message
    """
    try:
        # Setup Tesseract
        if not setup_tesseract():
            return "Error: Tesseract OCR not found. Please install Tesseract OCR and add it to PATH"
        
        # Check Urdu language availability
        if not check_urdu_language():
            return "Error: Urdu language pack not found. Please install urd.traineddata"
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Optional preprocessing: apply thresholding for better OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(thresh, lang='urd')
        
        if not text.strip():
            return "No text detected in the image"
        
        return text.strip()
        
    except Exception as e:
        return f"Error processing image: {str(e)}"
