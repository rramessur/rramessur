import requests

def test_extract():
    url = 'http://127.0.0.1:5000/extract'
    files = [
        ('files', ('test_form.pdf', open('test_form.pdf', 'rb'), 'application/pdf'))
    ]
    try:
        response = requests.post(url, files=files)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_extract()
