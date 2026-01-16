import sys
from pypdf import PdfReader

def analyze_pdf(pdf_path):
    print(f"Analyzing: {pdf_path}")
    reader = PdfReader(pdf_path)
    
    print("\n--- 1. Standard get_fields() ---")
    fields = reader.get_fields()
    if fields:
        for k, v in fields.items():
            print(f"Field: {k}, Type: {v.get('/FT')}, Value: {v.get('/V')}")
    else:
        print("No fields found via get_fields().")
        
    print("\n--- 2. Low-Level Page Annotation Scan ---")
    # Sometimes fields are detached widgets not in the main AcroForm tree
    total_widgets = 0
    for i, page in enumerate(reader.pages):
        print(f"Page {i+1}:")
        if '/Annots' in page:
            for annot in page['/Annots']:
                obj = annot.get_object()
                subtype = obj.get('/Subtype')
                if subtype == '/Widget':
                    total_widgets += 1
                    t = obj.get('/T')
                    ft = obj.get('/FT')
                    parent = obj.get('/Parent')
                    
                    # Try to resolve Name from parent if missing
                    if not t and parent:
                        parent_obj = parent.get_object()
                        t = f"[Parent] {parent_obj.get('/T')}"
                        
                    print(f"  - Widget: T={t}, FT={ft}, ID={obj.indirect_reference}")
                    
                    # Check extraction logic
                    is_btn = ft == '/Btn' or (parent and parent.get_object().get('/FT') == '/Btn')
                    if is_btn:
                        print(f"    -> IS CHECKBOX/RADIO. State: {obj.get('/AS')}")
        else:
            print("  No Annotations.")
            
    print(f"\nTotal Widgets Found: {total_widgets}")
            
    print("\n--- 3. missing Fields Analysis ---")
    standard_keys = set(fields.keys()) if fields else set()
    
    # Re-scan to find missing
    missing_count = 0
    for i, page in enumerate(reader.pages):
        if '/Annots' in page:
            for annot in page['/Annots']:
                obj = annot.get_object()
                if obj.get('/Subtype') == '/Widget':
                    t = obj.get('/T')
                    parent = obj.get('/Parent')
                    if not t and parent:
                        parent_obj = parent.get_object()
                        t = parent_obj.get('/T')
                        
                    if t and t not in standard_keys:
                         # Sometimes pypdf uses full qualified names, check if T is just a leaf
                         print(f"MISSING FROM STANDARD: {t} (FT={obj.get('/FT')})")
                         missing_count += 1
                         
    if missing_count == 0:
        print("No missing fields detected. (Maybe the user means it's extracted but empty?)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_structure.py <pdf_file>")
    else:
        analyze_pdf(sys.argv[1])
