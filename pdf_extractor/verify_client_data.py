import sys
import io
import csv
from pypdf import PdfReader
from utils import fill_pdf, parse_csv

def verify_fill(csv_path, pdf_path):
    print(f"Verifying CSV: {csv_path}")
    print(f"Against PDF: {pdf_path}")
    
    # Load CSV
    with open(csv_path, 'rb') as f:
        data = parse_csv(f)
        
    print(f"Loaded {len(data)} rows from CSV.")
    if not data:
        print("Error: No data found in CSV.")
        return

    # Load PDF Template
    with open(pdf_path, 'rb') as f:
        template_bytes = f.read()
        
    # Process First 5 Rows
    for i, row in enumerate(data[:5]):
        print(f"\n--- Checking Row {i+1} ---")
        print(f"CSV Data Sample: Clinic='{row.get('Clinic', 'N/A')}', Gender='{row.get('Gender', 'N/A')}'")
        
        # Fill
        filled_bytes = fill_pdf(template_bytes, row)
        
        if not filled_bytes:
            print("ERROR: Fill failed (returned None).")
            continue
            
        # Inspect Result
        reader = PdfReader(io.BytesIO(filled_bytes))
        
        # Check specific fields
        found_clinic = False
        found_gender = False
        
        for p_idx, page in enumerate(reader.pages):
            if '/Annots' not in page: continue
            for annot in page['/Annots']:
                obj = annot.get_object()
                if obj.get('/Subtype') != '/Widget': continue
                
                t = obj.get('/T')
                # Clinic (Parent) or Kids?
                # Usually standard extraction checks parents.
                # Let's interact with low level check
                
                # Check Clinic
                # Clinic is a Parent /Btn. We need to check if ANY kid is On.
                # OR pypdf might merge it?
                # Let's check the Widget that matches the expected value.
                
                # We can't easily check "Clinic" state without traversing Kids.
                # Detailed check: Check extraction results
                pass

        # Use pypdf extraction to verify "What is the value?"
        # get_fields() returns /V or /AS
        fields = reader.get_fields()
        
        clinic_val = fields.get('Clinic', {}).get('/V', 'Unset')
        gender_val = fields.get('Gender', {}).get('/V', 'Unset')
        
        print(f"  [PDF Result] Clinic: {clinic_val}")
        print(f"  [PDF Result] Gender: {gender_val}")
        
        # Validation Logic
        expected_clinic = row.get('Clinic')
        if expected_clinic:
             # loose check
             if str(clinic_val).strip('/') == 'Off' and expected_clinic:
                 print("  WARNING: Clinic is '/Off' (Not Ticked)!")
             else:
                 print("  SUCCESS: Clinic appears set (or at least not Off).")
                 
        expected_gender = row.get('Gender')
        if expected_gender:
             if str(gender_val).strip('/') == 'Off' and expected_gender:
                 print("  WARNING: Gender is '/Off' (Not Ticked)!")
             else:
                 print("  SUCCESS: Gender appears set.")

if __name__ == "__main__":
    verify_fill("Cally referrals for generation_clinic_codes_correct.csv", "gos_test_form.pdf")
