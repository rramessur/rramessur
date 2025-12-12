import csv
import random
import io
import zipfile
from pypdf import PdfReader, PdfWriter

def parse_csv(file_stream):
    """
    Parses a CSV file stream into a list of dictionaries.
    """
    try:
        # Decode bytes to string
        text = file_stream.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []

def match_data(demographics, clinical):
    """
    Randomly matches demographics with clinical data.
    Returns a list of merged dictionaries.
    """
    random.shuffle(demographics)
    random.shuffle(clinical)
    
    matched = []
    # Loop through the shorter list to ensure valid pairs
    count = min(len(demographics), len(clinical))
    
    for i in range(count):
        # Merge dictionaries
        merged = {**demographics[i], **clinical[i]}
        matched.append(merged)
        
    return matched

def apply_chaos(data_list):
    """
    Randomly removes fields from 30% of the records.
    Fields to target: NHS number, Gender, Address, Postcode
    Assumes keys in data match these names roughly or exactly.
    We'll look for case-insensitive matches for flexibility.
    """
    targets = ['nhs number', 'gender', 'address', 'postcode']
    
    # Calculate how many to affect
    num_to_affect = int(len(data_list) * 0.3)
    if num_to_affect == 0 and len(data_list) > 0:
         # Ensure at least one is affected if list is small but non-zero, 
         # or strictly stick to int conversion? Let's stick to int conversion (floor).
         pass

    indices = random.sample(range(len(data_list)), num_to_affect)
    
    for idx in indices:
        item = data_list[idx]
        # Pick one target to remove
        target_to_remove = random.choice(targets)
        
        # Find the actual key in the item that matches our target
        key_to_delete = None
        for key in item.keys():
            if target_to_remove in key.lower():
                key_to_delete = key
                break
        
        if key_to_delete:
            item[key_to_delete] = "" # Blank it out
            
    return data_list

def fill_pdf(template_bytes, data):
    """
    Fills a PDF template with data.
    Returns bytes of the filled PDF.
    """
    reader = PdfReader(io.BytesIO(template_bytes))
    writer = PdfWriter()

    try:
        # Copy pages and update form fields
        writer.append(reader)
            
        # Update fields
        # Note: update_page_form_field_values is deprecated or complex in newer pypdf
        # We work with the root writer object
        
        # Prepare data: values must be strings
        clean_data = {k: str(v) if v is not None else "" for k, v in data.items()}
        
        writer.update_page_form_field_values(
            writer.pages[0], clean_data#, auto_regenerate=False
        )

        output_stream = io.BytesIO()
        writer.write(output_stream)
        return output_stream.getvalue()
        
    except Exception as e:
        print(f"Error filling PDF: {e}")
        return None

def create_zip(pdf_files):
    """
    Creates a ZIP file containing the provided PDF files.
    pdf_files: list of (filename, bytes) tuples
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in pdf_files:
            zip_file.writestr(filename, content)
            
    return zip_buffer.getvalue()
