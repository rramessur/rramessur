from pypdf import PdfReader

reader = PdfReader("test_form.pdf")
fields = reader.get_fields()

print("Field Analysis:")
for key, value in fields.items():
    if '/FT' in value and value['/FT'] == '/Btn':
        print(f"Checkbox/Button: {key}")
        print(f"  Value: {value.get('/V')}")
        print(f"  Kids: {value.get('/Kids')}")
        # Try to find appearance states via /AP or similar if standard lookup fails, 
        # but pypdf usually exposes options in '/Opt' or implicit via widget annotation.
        # Actually, for checkboxes, we look for /N dictionary keys in /AP
        try:
             # Iterate through widgets to find On value
             if '/Kids' in value:
                 # This is a radio group or multiple checks
                 pass
             
             # Check widget directly if it's there
             # This is a deep dive, simpler:
             pass
        except:
             pass
             
    # Simplified dumping
    print(f"{key}: {value}")
