from utils import clean_value, parse_csv
import io
import unittest

class TestCleaning(unittest.TestCase):
    def test_clean_value(self):
        self.assertEqual(clean_value('="123"'), '123')
        self.assertEqual(clean_value('"123"'), '123')
        self.assertEqual(clean_value('123'), '123')
        self.assertEqual(clean_value(' =" 123 " '), '123 ') # whitespace then equals? My logic trims first.
        # " =" 123 " ".strip() -> '=" 123 "'. 
        
    def test_parse_csv_cleaning(self):
        csv_content = """name,value
test,="123"
test2,"456"
"""
        stream = io.BytesIO(csv_content.encode('utf-8'))
        results = parse_csv(stream)
        
        self.assertEqual(results[0]['value'], '123')
        self.assertEqual(results[1]['value'], '456')

if __name__ == '__main__':
    unittest.main()
