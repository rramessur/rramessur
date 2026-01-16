from pypdf import PdfReader
import sys

def inspect_clinic(pdf_path):
    reader = PdfReader(pdf_path)
    
    print("\n--- Inspecting 'Clinic' Field ---")
    fields = reader.get_fields()
    if 'Clinic' in fields:
        f = fields['Clinic']
        print(f"Type: {f.get('/FT')}")
        print(f"Flags: {f.get('/Ff')}")
        print(f"Kids: {len(f.get('/Kids', []))}")
        
        # Check Kids (the actual checkboxes/radio buttons)
        if '/Kids' in f:
            for i, kid in enumerate(f['/Kids']):
                k_obj = kid.get_object()
                print(f"  Kid {i+1}:")
                # The 'On' state is found in the Appearance Dictionary (/N) of the widget
                ap = k_obj.get('/AP', {}).get('/N', {})
                states = list(ap.keys())
                clean_states = [s for s in states if s != '/Off']
                print(f"    States: {clean_states}")
                print(f"    Rect: {k_obj.get('/Rect')}")
    else:
        print("'Clinic' field not found!")

    print("\n--- Searching for 'Children' or 'Adults' in all objects ---")
    # Scan all pages for any annotation with these words in Tooltip (/TU) or Contents
    for i, page in enumerate(reader.pages):
        if '/Annots' in page:
             for annot in page['/Annots']:
                 obj = annot.get_object()
                 tu = obj.get('/TU', '')
                 contents = obj.get('/Contents', '')
                 t = obj.get('/T', '')
                 
                 found = False
                 if 'child' in str(tu).lower() or 'child' in str(contents).lower(): found = True
                 if 'adult' in str(tu).lower() or 'adult' in str(contents).lower(): found = True
                 
                 if found:
                     print(f"Match found in Annot (Page {i+1}):")
                     print(f"  T: {t}")
                     print(f"  TU: {tu}")
                     print(f"  Contents: {contents}")

if __name__ == "__main__":
    inspect_clinic(sys.argv[1])
