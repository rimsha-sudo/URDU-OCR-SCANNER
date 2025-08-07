from pdf2image import convert_from_path
import os
import tempfile

def pdf_to_images(pdf_path, dpi=300):
    """
    Convert PDF to images
    
    Args:
        pdf_path (str): Path to the PDF file
        dpi (int): DPI for image conversion (default: 300)
        
    Returns:
        list: List of PIL Image objects or error message
    """
    try:
        # to check if file exists
        if not os.path.exists(pdf_path):
            return "Error PDF file not found"
        
        # to check if file is actually a PDF
        if not pdf_path.lower().endswith('.pdf'):
            return "Error File is not a PDF"
        
        # Conversion PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        if not images:
            return "Error Could not extract images from PDF"
        
        return images
        
    except Exception as e:
        return f"Error converting PDF: {str(e)}"

def pdf_to_images_from_bytes(pdf_bytes, dpi=300):
    """
    Convert PDF bytes to images
    
    Args:
        pdf_bytes (bytes): PDF file content as bytes
        dpi (int): DPI for image conversion (default: 300)
        
    Returns:
        list: List of PIL Image objects or error message
    """
    try:
        # Creating a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Conversiiiion PDF to images
        images = convert_from_path(tmp_file_path, dpi=dpi)
        
        # Cleaning temporary file
        os.unlink(tmp_file_path)
        
        if not images:
            return "Error Could not extract images from PDF"
        
        return images
        
    except Exception as e:
        return f"Error converting PDF: {str(e)}"
