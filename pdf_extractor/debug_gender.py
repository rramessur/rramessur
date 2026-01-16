from pypdf import PdfReader
import sys

def inspect_gender(pdf_path):
    reader = PdfReader(pdf_path)
    
    print("\n--- Inspecting 'Gender' Field ---")
    fields = reader.get_fields()
    if 'Gender' in fields:
        f = fields['Gender']
        print(f"Type: {f.get('/FT')}")
        print(f"Kids: {len(f.get('/Kids', []))}")
        
        # Check Kids
        if '/Kids' in f:
            for i, kid in enumerate(f['/Kids']):
                k_obj = kid.get_object()
                print(f"  Kid {i+1}:")
                ap = k_obj.get('/AP', {}).get('/N', {})
                states = list(ap.keys())
                clean_states = [s for s in states if s != '/Off']
                print(f"    States: {clean_states}")
                print(f"    Rect: {k_obj.get('/Rect')}")
    else:
        print("'Gender' field not found!")

if __name__ == "__main__":
    inspect_gender(sys.argv[1])
