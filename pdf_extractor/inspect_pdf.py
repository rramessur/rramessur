from pypdf import PdfReader

reader = PdfReader("test_form.pdf")
fields = reader.get_fields()
if fields:
    for field_name in fields.keys():
        print(field_name)
else:
    print("No fields found")
