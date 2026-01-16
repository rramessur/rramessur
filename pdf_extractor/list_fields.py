from pypdf import PdfReader
import sys

reader = PdfReader(sys.argv[1])
fields = reader.get_fields()
if fields:
    print(f"Found {len(fields)} fields:")
    for name in sorted(fields.keys()):
        ft = fields[name].get('/FT')
        print(f"- {name} ({ft})")
else:
    print("No fields found.")
