import streamlit as st
from main import extract_urdu_text, extract_urdu_text_from_pil_image, setup_tesseract, check_urdu_language, calculate_accuracy
from pdf_handler import pdf_to_images_from_bytes
from PIL import Image
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="Urdu OCR System",
    layout="wide"
)

# Title and description
st.title("Urdu OCR System")
st.markdown("Upload an image or PDF containing Urdu text to extract and convert it to editable text.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Tesseract installation Check
    if not setup_tesseract():
        st.error("Tesseract OCR not found!")
        st.info("Please install Tesseract OCR and add it to your system PATH")
        st.stop()
    
    # TO Check Urdu language pack
    if not check_urdu_language():
        st.error("Urdu language pack not found!")
        st.info("Please download urd.traineddata and place it in your Tesseract tessdata folder")
        st.stop()
    
    st.success("Tesseract OCR and Urdu language pack are properly configured!")
    
    # DPI setting for PDF processing
    dpi = st.slider("PDF Processing DPI", min_value=150, max_value=600, value=300, step=50)
    st.caption("Higher DPI = Better quality but slower processing")
    
    # Accuracy measurement toggle
    st.header("Accuracy Measurement")
    enable_accuracy = st.checkbox("Enable Accuracy Measurement", help="Compare extracted text with reference text")
    
    if enable_accuracy:
        st.info("Enter the correct/reference text to measure OCR accuracy")

# File upload section
uploaded_file = st.file_uploader(
    "Choose an image or PDF file", 
    type=["png", "jpg", "jpeg", "pdf"],
    help="Supported formats: PNG, JPG, JPEG, PDF"
)

# Reference text input for accuracy measurement
reference_text = ""
if enable_accuracy:
    st.subheader("Reference Text")
    reference_text = st.text_area(
        "Enter the correct text (for accuracy measurement):",
        height=150,
        help="Enter the exact text that should be in the image/PDF to measure OCR accuracy"
    )

if uploaded_file is not None:
    # to ddisplay file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB",
        "File type": uploaded_file.type
    }
    
    with st.expander("File Information"):
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
    
    # Processing of the file
    if uploaded_file.name.lower().endswith('.pdf'):
        st.subheader("Processing PDF")
        
        with st.spinner("Converting PDF to images"):
            # Conversion of  PDF to images
            images = pdf_to_images_from_bytes(uploaded_file.read(), dpi=dpi)
            
            if isinstance(images, str) and images.startswith("Error"):
                st.error(images)
            else:
                st.success(f"Successfully extracted {len(images)} page(s) from PDF")
                
                # Processing each page
                #Basically this is because if a pdf have more han one page it wil process each page one by one and will extract the
                #text one by one from each image then will send it further for more processing
                for i, img in enumerate(images):
                    st.markdown(f"### Page {i+1}")
                    
                    # Displaying the image
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.image(img, caption=f"Page {i+1}", use_container_width=True)
                    
                    with col2:
                        with st.spinner(f"Extracting text from page {i+1}..."):
                            # Extraction of text from the image
                            text = extract_urdu_text_from_pil_image(img)
                            
                            if text.startswith("Error"):
                                st.error(text)
                            elif text == "No text detected in the image":
                                st.warning("No Urdu text detected on this page")
                            else:
                                st.success("Text extracted successfully!")
                                st.text_area(
                                    f"Extracted Text (Page {i+1})", 
                                    value=text, 
                                    height=200,
                                    key=f"text_area_{i}"
                                )
                                # So for accuracy what I did was I made these comparision metrics which is that for the accuracy of text if you want 
                                # you can give the actual text and then let the system extract the text and on the basis of the original and extarcted 
                                #text , you can evaluate the accuracy
                                # Accuracy measurement
                                if enable_accuracy and reference_text:
                                    st.subheader("Accuracy Analysis")
                                    accuracy_results = calculate_accuracy(text, reference_text)
                                    
                                    # Displaying  accuracy metrics
                                    col_acc1, col_acc2, col_acc3, col_acc4 = st.columns(4)
                                    
                                    with col_acc1:
                                        st.metric("Overall Accuracy", f"{accuracy_results['overall_accuracy']}%")
                                    
                                    with col_acc2:
                                        st.metric("Character Accuracy", f"{accuracy_results['character_accuracy']}%")
                                    
                                    with col_acc3:
                                        st.metric("Word Accuracy", f"{accuracy_results['word_accuracy']}%")
                                    
                                    with col_acc4:
                                        st.metric("Similarity Score", f"{accuracy_results['similarity_score']}%")
                                    
                                    # Moore detailed analysis
                                    with st.expander("Detailed Analysis"):
                                        st.write(f"**Extracted text length:** {accuracy_results['extracted_length']} characters")
                                        st.write(f"**Reference text length:** {accuracy_results['reference_length']} characters")
                                        
                                        if accuracy_results['missing_words']:
                                            st.write(f"**Missing words:** {', '.join(accuracy_results['missing_words'][:10])}")
                                        
                                        if accuracy_results['extra_words']:
                                            st.write(f"**Extra words:** {', '.join(accuracy_results['extra_words'][:10])}")
                                        
                                        st.write(f"**Error details:** {accuracy_results['error_details']}")
                    
                    st.divider()
    
    else:
        st.subheader("Processing Image")
        
        # Display the uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        
        with col2:
            with st.spinner("Extracting Urdu text"):
                # Extract text directly from PIL image
                text = extract_urdu_text_from_pil_image(image)
                
                if text.startswith("Error"):
                    st.error(text)
                elif text == "No text detected in the image":
                    st.warning("No Urdu text detected in the image")
                else:
                    st.success("Text extracted successfully!")
                    st.text_area(
                        "Extracted Urdu Text", 
                        value=text, 
                        height=300,
                        key="extracted_text"
                    )
                    
                    # Accuracy measurement
                    if enable_accuracy and reference_text:
                        st.subheader("Accuracy Analysis")
                        accuracy_results = calculate_accuracy(text, reference_text)
                        
                        # Display accuracy metrics
                        col_acc1, col_acc2, col_acc3, col_acc4 = st.columns(4)
                        
                        with col_acc1:
                            st.metric("Overall Accuracy", f"{accuracy_results['overall_accuracy']}%")
                        
                        with col_acc2:
                            st.metric("Character Accuracy", f"{accuracy_results['character_accuracy']}%")
                        
                        with col_acc3:
                            st.metric("Word Accuracy", f"{accuracy_results['word_accuracy']}%")
                        
                        with col_acc4:
                            st.metric("Similarity Score", f"{accuracy_results['similarity_score']}%")
                        
                        # Detailed analysis
                        with st.expander("Detailed Analysis"):
                            st.write(f"**Extracted text length:** {accuracy_results['extracted_length']} characters")
                            st.write(f"**Reference text length:** {accuracy_results['reference_length']} characters")
                            
                            if accuracy_results['missing_words']:
                                st.write(f"**Missing words:** {', '.join(accuracy_results['missing_words'][:10])}")
                            
                            if accuracy_results['extra_words']:
                                st.write(f"**Extra words:** {', '.join(accuracy_results['extra_words'][:10])}")
                            
                            st.write(f"**Error details:** {accuracy_results['error_details']}")
                    
                    # Added download button for extracted text if you want to copy paste it somewhere
                    st.download_button(
                        label="Download Text",
                        data=text,
                        file_name="extracted_urdu_text.txt",
                        mime="text/plain"
                    )

# Add footer with instructions
st.markdown("---")
st.markdown("""
### Instructions:
1. **For Images**: Upload PNG, JPG, or JPEG files containing Urdu text
2. **For PDFs**: Upload PDF files - each page will be processed separately
3. **Text Quality**: Ensure the text is clear and well-lit for better results
4. **Language**: The system is optimized for Urdu text recognition
5. **Accuracy Measurement**: Enable in sidebar and enter reference text to measure OCR accuracy

### Troubleshooting:
- If no text is detected, try uploading a higher quality image
- For PDFs, try adjusting the DPI setting in the sidebar
- Make sure the text is clearly visible and not too small
- For accuracy measurement, enter the exact text that should be in the image

### Accuracy Metrics:
- **Overall Accuracy**: Weighted combination of all metrics
- **Character Accuracy**: Percentage of correctly recognized characters
- **Word Accuracy**: Percentage of correctly recognized words
- **Similarity Score**: Overall text similarity using sequence matching
""")
