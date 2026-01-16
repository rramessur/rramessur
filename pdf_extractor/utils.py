import csv
import random
import io
import zipfile
from pypdf import PdfReader, PdfWriter

def clean_value(value):
    """
    Removes Excel-style escaping (e.g. ='...', "...") and stripping whitespace.
    """
    if value is None:
        return ""
    
    val = str(value).strip()
    
    # Remove Excel protection like ="value"
    if val.startswith('="') and val.endswith('"'):
        val = val[2:-1]
    
    # Remove surrounding quotes if present
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
        
    return val

def parse_csv(file_stream):
    """
    Parses a CSV file stream into a list of dictionaries.
    """
    try:
        # Decode bytes to string
        text = file_stream.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        
        # Parse and clean
        results = []
        for row in reader:
            cleaned_row = {
                k: clean_value(v) 
                for k, v in row.items()
            }
            results.append(cleaned_row)
            
        return results
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []

def match_data(demographics, clinical):
    """
    Randomly matches demographics with clinical data.
    Returns a list of merged dictionaries.
    """
    random.shuffle(demographics)
    random.shuffle(clinical)
    
    matched = []
    # Loop through the shorter list to ensure valid pairs
    count = min(len(demographics), len(clinical))
    
    for i in range(count):
        # Merge dictionaries
        merged = {**demographics[i], **clinical[i]}
        matched.append(merged)
        
    return matched

def apply_chaos(data_list):
    """
    Randomly removes fields from 30% of record.
    Fields to target: NHS number, Gender, Address, Postcode
    """
    targets = ['nhs number', 'gender', 'address', 'postcode']
    
    # Calculate how many to affect
    num_to_affect = int(len(data_list) * 0.3)
    if num_to_affect == 0 and len(data_list) > 0:
         pass

    indices = random.sample(range(len(data_list)), num_to_affect)
    
    for idx in indices:
        item = data_list[idx]
        # Pick one target to remove
        target_to_remove = random.choice(targets)
        
        # Find the actual key in the item that matches our target
        key_to_delete = None
        for key in item.keys():
            if target_to_remove in key.lower():
                key_to_delete = key
                break
        
        if key_to_delete:
            item[key_to_delete] = "" # Blank it out
            
    return data_list

from pypdf.generic import NameObject, TextStringObject, BooleanObject

def fill_pdf(template_bytes, data):
    """
    Fills a PDF template with data.
    Returns bytes of the filled PDF.
    """
    reader = PdfReader(io.BytesIO(template_bytes))
    writer = PdfWriter()

    try:
        writer.append(reader)
        
        # 1. Map Field Names to Data.
        # ... (rest is unchanged)
        # We need a quick lookup of what values we want to set.
        # Clean keys to match what we might find in the PDF (simple matching)
        data_map = {k.lower(): v for k, v in data.items()}
        
        # 2. Iterate over all pages and their annotations (Widgets)
        for page in writer.pages:
            if '/Annots' not in page:
                continue
                
            for annot in page['/Annots']:
                obj = annot.get_object()
                
                # We are looking for Widget annotations (Interactive Forms)
                if obj.get('/Subtype') != '/Widget':
                    continue
                    
                # Resolve Field Name
                # It might be on the object itself or its parent
                field_name = obj.get('/T')
                parent = obj.get('/Parent')
                
                # If no name, traverse up potentially (simplified here)
                # Radio groups: Parent has /T (e.g. "Gender"), Kids have no /T usually.
                active_obj = obj
                if not field_name and parent:
                    parent_obj = parent.get_object()
                    field_name = parent_obj.get('/T')
                    active_obj = parent_obj
                    
                if not field_name:
                    continue
                    
                # Match against our data
                # Handle standard string/bytes returned by pypdf
                key = str(field_name).strip()
                if key.lower() not in data_map:
                    continue
                    
                user_value = data_map[key.lower()]
                
                # 3. Determine Field Type and Update Logic
                # Check FT on widget or parent
                ft = obj.get('/FT') or active_obj.get('/FT')
                
                # === Text Fields ===
                if ft == '/Tx':
                    # easy: just set /V
                    val_str = str(user_value)
                    active_obj[NameObject('/V')] = TextStringObject(val_str)
                    
                    # Also update appearance if possible (simplified: pypdf might need need_appearances flag)
                    # We often need to reset AP to force regeneration
                    if '/AP' in obj:
                        del obj['/AP']
                        
                # === Buttons (Checkboxes / Radio) ===
                elif ft == '/Btn':
                    # Goal: Set /V on Parent/Field AND /AS on Widget
                    
                    # A. Analyze Appearance States for THIS widget
                    valid_states = set()
                    ap = obj.get('/AP', {})
                    if isinstance(ap, dict):
                        n_ap = ap.get('/N', {})
                        if isinstance(n_ap, dict):
                            valid_states.update(n_ap.keys())
                            
                    # Remove /Off
                    on_states = {s for s in valid_states if s != '/Off'}
                    
                    # B. Determine Desired State based on user input
                    target_state = NameObject('/Off')
                    
                    val_str = str(user_value).strip()
                    val_lower = val_str.lower()
                    
                    # Direct Match (e.g. CSV "Male" -> matches state "/Male")
                    match_found = False
                    
                    # Helper to normalize string (remove non-alphanumeric, lowercase)
                    def normalize(s):
                        import re
                        return re.sub(r'[^a-z0-9]', '', str(s).lower())

                    val_norm = normalize(user_value)
                    
                    for state in on_states:
                        state_name = state.replace('/', '')
                        state_norm = normalize(state_name)
                        
                        # 1. Exact Normal Match (Handles "Child - Strab" == "Child-Strab")
                        if val_norm == state_norm:
                            target_state = NameObject(state)
                            match_found = True
                            break
                            
                        # 2. Contains Match (Handles "Female" in "Female Patient", or "Oculoplastics" in "Oculoplastics / Orbits")
                        # Use strictly state in value (PDF option is usually the substring)
                        if len(state_norm) > 3 and state_norm in val_norm:
                            target_state = NameObject(state)
                            match_found = True
                            break
                            
                    # Fuzzy / Generic Match (CSV "Yes" -> matches any on state)
                    if not match_found and val_lower in ['yes', 'true', '1', 'on', 'checked', 'x']:
                         if on_states:
                             # Pick first one (e.g. /Yes, /On, /Male)
                             # Prefer /Yes or /On if available
                             best = list(on_states)[0]
                             for s in on_states:
                                 if s in ['/Yes', '/On']:
                                     best = s
                                     break
                             target_state = NameObject(best)
                             match_found = True
                    
                    # C. Update Objects
                    
                    # Update Widget Appearance (/AS)
                    if target_state in valid_states:
                         obj[NameObject('/AS')] = target_state
                    else:
                         # This widget doesn't have the target state (so it's a sibling in a radio group)
                         # Set it to Off
                         obj[NameObject('/AS')] = NameObject('/Off')
                    
                    # Update Field Value (/V) - usually on Parent
                    # CRITICAL FIX: Only set V if we found a POSITIVE match.
                    # Do not overwrite V with /Off just because *this specific widget* isn't the one enabled.
                    # In a radio group, 14 widgets are Off, 1 is On. We don't want the 14 Offs to erase the 1 On.
                    if match_found:
                         active_obj[NameObject('/V')] = target_state

                # === Choice Fields (Dropdowns / Listboxes) ===
                elif ft == '/Ch':
                    # Just like Text, but value must (usually) be one of the options.
                    # We will trust the user value, but we could validate against /Opt if needed.
                    val_str = str(user_value)
                    
                    # Set value
                    active_obj[NameObject('/V')] = TextStringObject(val_str)
                    
                    # For combo boxes with editing enabled, this is enough.
                    # For strict lists, if val_str isn't in /Opt, it might not show.
                    # We assume user inputs valid data or 'custom' text is allowed if 'Edit' flag is on.
                    
                    # Reset appearance to force regeneration by viewer
                    if '/AP' in obj:
                        del obj['/AP']

        # Force NeedAppearances so viewers re-render text
        # (Checkboxes usually rely on /AS so they are fine, but Text needs this usually if we del /AP)
        if '/AcroForm' not in writer.root_object:
            writer.root_object.update({
                NameObject("/AcroForm"): writer._create_object_stream(
                    {NameObject("/NeedAppearances"): BooleanObject(True)}
                )
            })
        else:
             af = writer.root_object['/AcroForm']
             # af could be IndirectObject or DictionaryObject
             # writer.get_object() expects IndirectObject
             if hasattr(af, 'pdf'): # Heuristic for IndirectObject which usually has .pdf ref or similar, or just try/except
                 af_obj = writer.get_object(af)
             else:
                 af_obj = af
                 
             af_obj.update({
                 NameObject("/NeedAppearances"): BooleanObject(True)
             })

        output_stream = io.BytesIO()
        writer.write(output_stream)
        return output_stream.getvalue()
        
    except Exception as e:
        print(f"Error filling PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_zip(pdf_files):
    """
    Creates a ZIP file containing the provided PDF files.
    pdf_files: list of (filename, bytes) tuples
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in pdf_files:
            zip_file.writestr(filename, content)
            
    return zip_buffer.getvalue()
