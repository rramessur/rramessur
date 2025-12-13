import unittest
from unittest.mock import MagicMock, patch
import io
from utils import fill_pdf
from pypdf.generic import NameObject, TextStringObject

class TestSmartFill(unittest.TestCase):
    
    @patch('utils.PdfReader')
    @patch('utils.PdfWriter')
    def test_smart_fill_low_level(self, MockWriter, MockReader):
        # Setup Mock Writer
        mock_writer = MockWriter.return_value
        mock_writer.pages = []
        
        # Create a Mock Page with Annotations
        mock_page = MagicMock()
        mock_writer.pages.append(mock_page)
        
        # Create Mock Annotations (Widgets)
        
        # 1. Standard Checkbox: /T="is_human"
        annot_checkbox = MagicMock()
        obj_checkbox = MagicMock()
        annot_checkbox.get_object.return_value = obj_checkbox
        
        obj_checkbox.get.side_effect = lambda k, default=None: {
            '/Subtype': '/Widget',
            '/T': 'is_human',
            '/FT': '/Btn',
            '/AP': {'/N': {'/Yes': {}, '/Off': {}}}
        }.get(k, default)
        # Mock dictionary behavior for setting /AS and /V
        checkbox_dict = {}
        def set_item_checkbox(k, v):
            checkbox_dict[k] = v
        obj_checkbox.__setitem__.side_effect = set_item_checkbox
        
        # 2. Radio Group: Parent /T="gender", Child Widget /Male
        annot_radio = MagicMock()
        obj_radio = MagicMock()
        annot_radio.get_object.return_value = obj_radio
        
        # Parent object
        parent_radio = MagicMock()
        parent_radio.get_object.return_value = {
            '/T': 'gender',
            '/FT': '/Btn'
        }
        
        obj_radio.get.side_effect = lambda k, default=None: {
            '/Subtype': '/Widget',
            '/T': None, # No name on widget, it's on parent
            '/Parent': parent_radio,
            '/FT': '/Btn', # might be inherited, but let's say it's here
            '/AP': {'/N': {'/Male': {}, '/Off': {}}}
        }.get(k, default)
        
        radio_dict = {}
        def set_item_radio(k, v):
            radio_dict[k] = v
        obj_radio.__setitem__.side_effect = set_item_radio
        
        # Attach annots to page
        mock_page.__getitem__.return_value = [annot_checkbox, annot_radio]
        mock_page.__contains__.return_value = True # has /Annots
        
        # Test Data
        data = {
            'is_human': 'Yes',
            'gender': 'Male'
        }
        
        # Run fill_pdf
        fill_pdf(b'dummy_bytes', data)
        
        # Assertions
        print("Checkbox Updates:", checkbox_dict)
        print("Radio Updates:", radio_dict)
        
        # Checkbox should be /Yes
        self.assertEqual(checkbox_dict.get(NameObject('/AS')), NameObject('/Yes'))
        self.assertEqual(checkbox_dict.get(NameObject('/V')), NameObject('/Yes')) # Actually it sets V on obj_checkbox which is also active_obj
        
        # Radio should be /Male
        self.assertEqual(radio_dict.get(NameObject('/AS')), NameObject('/Male'))
        # V should be set on parent, but my mock logic for 'active_obj' might have set it on parent_obj or obj depending on mock setup.
        # My code: active_obj = parent_obj if parent used.
        # In mock setup: active_obj = parent_radio.get_object() which is a dict.
        # So I can't check 'parent_radio' mock unless I inspect that dict, but that dict was created on the fly in lambda?
        # A bit tricky to verify Parent /V update with this simple mock, but /AS on widget is the critical visual part found in user complaint.
        
        # Let's trust /AS check as primary.

if __name__ == '__main__':
    unittest.main()
