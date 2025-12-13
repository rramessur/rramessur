import os
import io
import csv
from flask import Flask, render_template, request, jsonify, Response, send_file
from pypdf import PdfReader
from utils import parse_csv, match_data, apply_chaos, fill_pdf, create_zip

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient-matcher')
def patient_matcher():
    return render_template('patient_matcher.html')

@app.route('/generate-page')
def generate_page():
    return render_template('generate.html')

@app.route('/extract', methods=['POST'])
def extract_fields():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
            
        try:
            # Read file in memory
            pdf_bytes = io.BytesIO(file.read())
            reader = PdfReader(pdf_bytes)
            fields = reader.get_fields()
            
            field_data = {}
            if fields:
                for field_name, field_obj in fields.items():
                    # Extract value, handling different field types potentially
                    # pypdf fields are complex, we try to get '/V' (Value)
                    value = field_obj.get('/V', '')
                    
                    # Checkbox handling: Normalize /Yes to "Yes"
                    if field_obj.get('/FT') == '/Btn':
                        val_str = str(value)
                        if val_str == '/Yes' or val_str == '/On' or val_str == 'Yes' or val_str == 'On':
                            value = "Yes"
                        elif val_str == '/Off':
                             value = "No"
                        else:
                             # Fallback: if it looks like a NameObject with a slash, strip it?
                             # Or just valid truthy check?
                             if val_str.startswith('/') and len(val_str) > 1:
                                  # Heuristic: /Value -> Value
                                  value = val_str[1:]
                    
                    # Handle some common text cleanup
                    if isinstance(value, str):
                        value = value.strip()
                    field_data[field_name] = str(value) if value is not None else ""
            
            results.append({
                'filename': file.filename,
                'fields': field_data
            })
            
        except Exception as e:
            results.append({
                'filename': file.filename,
                'error': str(e)
            })

    return jsonify({'results': results})

@app.route('/generate', methods=['POST'])
def generate_pdfs():
    if 'demographics' not in request.files or 'clinical' not in request.files or 'template' not in request.files:
        return jsonify({'error': 'Missing required files (demographics, clinical, template)'}), 400
        
    demographics_file = request.files['demographics']
    clinical_file = request.files['clinical']
    template_file = request.files['template']
    
    try:
        # Parse CSVs
        demographics = parse_csv(demographics_file)
        clinical = parse_csv(clinical_file)
        
        if not demographics or not clinical:
             return jsonify({'error': 'Could not parse one or both CSV files'}), 400
             
        # Match data
        matched_data = match_data(demographics, clinical)
        
        # Apply chaos (30% missing fields)
        final_data = apply_chaos(matched_data)
        
        # Read template
        template_bytes = template_file.read()
        
        # Generator PDFs
        pdf_files = []
        for i, data in enumerate(final_data):
            # Use a unique filename
            # Try to use Name/ID if available, else index
            fname = f"patient_{i+1}.pdf"
            if 'first_name' in data and 'last_name' in data: # Example assumption
                 fname = f"{data['first_name']}_{data['last_name']}_{i+1}.pdf".replace(" ", "_")
            
            filled_pdf = fill_pdf(template_bytes, data)
            if filled_pdf:
                pdf_files.append((fname, filled_pdf))
                
        if not pdf_files:
            return jsonify({'error': 'No PDFs could be generated'}), 500
            
        # Create ZIP
        zip_bytes = create_zip(pdf_files)
        
        return send_file(
            io.BytesIO(zip_bytes),
            mimetype='application/zip',
            as_attachment=True,
            download_name='generated_patients.zip'
        )
        
    except Exception as e:
        app.logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/direct-fill-page')
def direct_fill_page():
    return render_template('direct_fill.html')

@app.route('/direct-fill', methods=['POST'])
def direct_fill():
    if 'csv_file' not in request.files or 'template' not in request.files:
        return jsonify({'error': 'Missing required files (csv_file, template)'}), 400
        
    csv_file = request.files['csv_file']
    template_file = request.files['template']
    
    try:
        # Parse CSV
        data_rows = parse_csv(csv_file)
        
        if not data_rows:
             return jsonify({'error': 'Could not parse CSV file'}), 400
             
        # Read template
        template_bytes = template_file.read()
        
        # Generator PDFs
        pdf_files = []
        for i, row in enumerate(data_rows):
            # Use a unique filename
            # Try to use Name/ID/Filename keys if available
            fname = f"filled_{i+1}.pdf"
            
            # Heuristic for better naming
            for key in ['filename', 'id', 'name', 'patient_id']:
                # Case insensitive search in keys
                found_key = next((k for k in row.keys() if k.lower() == key), None)
                if found_key and row[found_key]:
                     fname = f"{row[found_key]}.pdf".replace(" ", "_")
                     break

            filled_pdf = fill_pdf(template_bytes, row)
            if filled_pdf:
                pdf_files.append((fname, filled_pdf))
                
        if not pdf_files:
            return jsonify({'error': 'No PDFs could be generated'}), 500
            
        # Create ZIP
        zip_bytes = create_zip(pdf_files)
        
        return send_file(
            io.BytesIO(zip_bytes),
            mimetype='application/zip',
            as_attachment=True,
            download_name='filled_forms.zip'
        )
        
    except Exception as e:
        app.logger.error(f"Direct fill error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
