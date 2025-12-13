from pypdf import PdfReader
import io

# Create a dummy PDF with a checkbox if possible, or just read existing 'test_form.pdf'
# I'll read 'test_form.pdf' assuming it has checkboxes. 
# If not, I rely on general pypdf knowledge: NameObject('/Yes') str() -> '/Yes'

reader = PdfReader("test_form.pdf")
fields = reader.get_fields()

if fields:
    for k, v in fields.items():
        if v.get('/FT') == '/Btn':
            val = v.get('/V')
            print(f"Key: {k}, Value: {val}, Type: {type(val)}")
            print(f"Str Value: {str(val)}")
