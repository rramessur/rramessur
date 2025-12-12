import unittest
import io
import zipfile
from app import app

class TestDirectFill(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_direct_fill_success(self):
        # Prepare mock files
        with open('test_direct_fill.csv', 'rb') as f:
            csv_content = f.read()
        
        with open('test_form.pdf', 'rb') as f:
            pdf_content = f.read()
            
        data = {
            'csv_file': (io.BytesIO(csv_content), 'test.csv'),
            'template': (io.BytesIO(pdf_content), 'template.pdf')
        }
        
        response = self.app.post('/direct-fill', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')
        
        # Verify ZIP content
        zip_buffer = io.BytesIO(response.data)
        with zipfile.ZipFile(zip_buffer) as z:
            file_names = z.namelist()
            self.assertEqual(len(file_names), 2)
            # filenames might be John.pdf or Jane.pdf based on heuristic (fname key)
            # or filled_1.pdf if heuristic fails.
            # In my csv header is 'fname', so heuristic might not catch it unless I update app.py or change csv header.
            # App.py heuristic looks for: 'filename', 'id', 'name', 'patient_id'. 'fname' is not there.
            # So it should be filled_1.pdf, filled_2.pdf?
            # Wait, let's check heuristics in app.py.
            
            # Heuristics: ['filename', 'id', 'name', 'patient_id']
            # My csv header: 'fname'. 
            # So names will be filled_1.pdf, filled_2.pdf.
            
            self.assertIn('filled_1.pdf', file_names)
            self.assertIn('filled_2.pdf', file_names)

if __name__ == '__main__':
    unittest.main()
