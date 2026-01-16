from pypdf import PdfReader
import sys

def inspect_gp_action(pdf_path):
    reader = PdfReader(pdf_path)
    
    print("\n--- Inspecting 'GP Action' Field ---")
    fields = reader.get_fields()
    if 'GP Action' in fields:
        f = fields['GP Action']
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
            # Maybe it's a single checkbox
            print("  Single Widget (No Kids)")
            # Get widget obj
            # pypdf fields are usually the dictionary itself if no kids
            ap = f.get('/AP', {}).get('/N', {})
            states = list(ap.keys())
            clean_states = [s for s in states if s != '/Off']
            print(f"    States: {clean_states}")
            
    else:
        print("'GP Action' field not found!")

if __name__ == "__main__":
    inspect_gp_action(sys.argv[1])
