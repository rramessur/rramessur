from pypdf import PdfReader

reader = PdfReader("test_form.pdf")
fields = reader.get_fields()

print("Deep Inspection of /Btn fields:")
if fields:
    for k, v in fields.items():
        if v.get('/FT') == '/Btn':
            print(f"Field: {k}")
            print(f"  Value (/V): {v.get('/V')}")
            print(f"  Default (/DV): {v.get('/DV')}")
            print(f"  Options (/Opt): {v.get('/Opt')}")
            # Try to get appearance keys which tell us the valid 'On' state names
            try:
                widgets = v.get('/Kids', [v])
                for w in widgets:
                    # Resolve indirect object if needed (pypdf usually does this)
                    ap = w.get('/AP', {})
                    n_ap = ap.get('/N', {})
                    print(f"  Appearance States (/AP/N): {list(n_ap.keys()) if hasattr(n_ap, 'keys') else n_ap}")
            except Exception as e:
                print(f"  Error inspecting widgets: {e}")
                
            print("-" * 20)
            
else:
    print("No fields found")
