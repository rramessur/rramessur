from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue, pink

def create_simple_form():
    c = canvas.Canvas('test_form.pdf')
    c.setFont("Helvetica", 12)
    
    c.drawString(10, 650, 'First Name:')
    
    # Create a form text field
    form = c.acroForm
    form.textfield(name='fname', tooltip='First Name',
                   x=110, y=635, borderStyle='inset',
                   borderColor=blue, fillColor=pink, 
                   width=300, height=20,
                   textColor=blue, forceBorder=True,
                   value='John Doe') # Pre-fill with value to test extraction
                   
    c.save()

if __name__ == "__main__":
    create_simple_form()
    print("Created test_form.pdf with ReportLab")
