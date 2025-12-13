from utils import fill_pdf
import io
from reportlab.pdfgen import canvas

def create_mock_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 100, "Hello")
    form = c.acroForm
    form.textfield(name='TestField', x=110, y=600, width=200, height=20)
    c.save()
    return buffer.getvalue()

mock_data = {'TestField': 'TestValue'}
pdf_bytes = create_mock_pdf()

print("Attempting to fill mock PDF...")
result = fill_pdf(pdf_bytes, mock_data)

if result:
    print("Success! PDF filled.")
else:
    print("Failed to fill PDF.")
