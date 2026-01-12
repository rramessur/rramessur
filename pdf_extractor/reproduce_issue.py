import requests
import io
import csv

def create_large_csv(rows=100):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['first_name', 'last_name', 'gender', 'nhs number'])
    for i in range(rows):
        writer.writerow([f'User{i}', f'Test{i}', 'Male', f'123456789{i}'])
    
    return io.BytesIO(output.getvalue().encode('utf-8'))

def create_mock_pdf():
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 100, "Hello")
    form = c.acroForm
    form.textfield(name='first_name', x=10, y=10, width=100, height=20)
    c.save()
    buffer.seek(0)
    return buffer

def reproduce():
    # Create large CSV (try 500 rows to see if it triggers issue)
    print("Creating large CSV (500 rows)...")
    csv_file = create_large_csv(500)
    pdf_file = create_mock_pdf()
    
    files = {
        'csv_file': ('large.csv', csv_file, 'text/csv'),
        'template': ('template.pdf', pdf_file, 'application/pdf')
    }
    
    print("Sending POST request to /direct-fill...")
    try:
        response = requests.post('http://localhost:5000/direct-fill', files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Response Content (First 500 chars):")
            print(response.text[:500])
        else:
            print("Success! Response is valid.")
            print(f"Content Type: {response.headers.get('Content-Type')}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    reproduce()
