import requests
import io
import zipfile
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue, pink

# 1. Create Mock Data
def create_mock_files():
    # Demographics
    demo_data = [
        ['first_name', 'last_name', 'gender', 'address', 'postcode'],
        ['John', 'Doe', 'Male', '123 Fake St', 'SW1A 1AA'],
        ['Jane', 'Smith', 'Female', '456 Real Rd', 'M1 1AA'],
        ['Bob', 'Jones', 'Male', '789 Test Ave', 'B1 1AA'],
        ['Alice', 'Williams', 'Female', '101 Dev Ln', 'L1 1AA'],
        ['Charlie', 'Brown', 'Male', '202 Null Dr', 'CF10 1AA'],
        ['Diana', 'Prince', 'Female', '303 Void Wy', 'EH1 1AA'],
        ['Evan', 'Wright', 'Male', '404 Err Pl', 'BT1 1AA'],
        ['Fiona', 'Green', 'Female', '505 Valid Rd', 'NE1 1AA'],
        ['George', 'Black', 'Male', '606 Null St', 'S1 1AA'],
        ['Hannah', 'White', 'Female', '707 Byte Ct', 'G1 1AA'],
    ]
    
    demo_csv = io.StringIO()
    writer = csv.writer(demo_csv)
    writer.writerows(demo_data)
    demo_bytes = io.BytesIO(demo_csv.getvalue().encode('utf-8'))
    demo_bytes.name = 'demographics.csv'
    
    # Clinical
    clin_data = [
        ['nhs number', 'diagnosis', 'medication'],
        ['1111111111', 'Flu', 'Paracetamol'],
        ['2222222222', 'Cold', 'Ibuprofen'],
        ['3333333333', 'Headache', 'Aspirin'],
        ['4444444444', 'Back Pain', 'Codeine'],
        ['5555555555', 'Fever', 'Water'],
        ['6666666666', 'Cough', 'Syrup'],
        ['7777777777', 'Sore Throat', 'Lozenges'],
        ['8888888888', 'Rash', 'Cream'],
        ['9999999999', 'Infection', 'Antibiotics'],
        ['0000000000', 'Anxiety', 'Therapy'],
    ]
    
    clin_csv = io.StringIO()
    writer = csv.writer(clin_csv)
    writer.writerows(clin_data)
    clin_bytes = io.BytesIO(clin_csv.getvalue().encode('utf-8'))
    clin_bytes.name = 'clinical.csv'
    
    # Template PDF with Form Fields
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(10, 650, 'First Name:')
    form = c.acroForm
    # Create fields matching our data keys (exact match required usually)
    # We used lowercase keys in CSV, assume map or exact match.
    # Script assumes 'first_name', 'last_name', 'gender', 'address', 'postcode', 'nhs number', etc.
    # Standard AcroForm fields.
    fields = [
        'first_name', 'last_name', 'gender', 'address', 'postcode',
        'nhs number', 'diagnosis', 'medication'
    ]
    
    y = 600
    for field in fields:
        form.textfield(name=field, tooltip=field,
                       x=110, y=y, width=200, height=20)
        c.drawString(10, y+5, field)
        y -= 30
        
    c.save()
    pdf_bytes = io.BytesIO(pdf_buffer.getvalue())
    pdf_bytes.name = 'template.pdf'
    
    return demo_bytes, clin_bytes, pdf_bytes

def test_generate_endpoint():
    print("Creating mock files...")
    demo, clin, tmpl = create_mock_files()
    
    files = {
        'demographics': demo,
        'clinical': clin,
        'template': tmpl
    }
    
    print("Sending POST request to /generate...")
    try:
        # Assuming app is running on port 5000
        response = requests.post('http://localhost:5000/generate', files=files)
        
        if response.status_code == 200:
            print("Success! Got 200 OK.")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            # Verify ZIP
            try:
                zip_buffer = io.BytesIO(response.content)
                with zipfile.ZipFile(zip_buffer) as z:
                    print(f"ZIP contains {len(z.namelist())} files.")
                    print("Files:", z.namelist())
                    
                    if len(z.namelist()) > 0:
                        # Extract one and check fields (pypdf)
                        from pypdf import PdfReader
                        
                        missing_count = 0
                        total_checked = 0
                        
                        targets = ['gender', 'address', 'postcode', 'nhs number'] # keys we expect might be missing

                        for fname in z.namelist():
                            with z.open(fname) as pdf_file:
                                reader = PdfReader(pdf_file)
                                fields = reader.get_fields()
                                # Check for missing values in target fields
                                # Note: pypdf get_fields returns dict of objects. Value is usually under '/V'
                                
                                if fields:
                                    # Count how many of our target fields are empty
                                    missing_in_this_file = 0
                                    for t in targets:
                                        if t in fields:
                                            val = fields[t].get('/V', '')
                                            if not val: # Empty string or None
                                                missing_in_this_file += 1
                                    
                                    if missing_in_this_file > 0:
                                        missing_count += 1
                                        print(f"File {fname} has missing fields.")
                                    
                                    total_checked += 1

                        print(f"\nFound missing data in {missing_count}/{total_checked} files.")
                        percentage = (missing_count / total_checked) * 100
                        print(f"Percentage with missing data: {percentage:.2f}% (Expected ~30%)")

            except zipfile.BadZipFile:
                print("Error: content is not a valid zip file.")
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure the Flask app is running!")

if __name__ == "__main__":
    test_generate_endpoint()
