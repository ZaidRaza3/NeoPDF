from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
from flask_cors import CORS
import io
import json
import zipfile
import os

app = Flask(__name__)
CORS(app)

# Helper function to parse page ranges (e.g., '1,3,5' or '2-4')
def parse_pages(page_str, total_pages):
    pages = set()
    parts = page_str.replace(' ', '').split(',')
    for part in parts:
        if '-' in part:
            start_end = part.split('-')
            start = int(start_end[0])
            end = int(start_end[1])
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted([p - 1 for p in pages if 0 <= p - 1 < total_pages])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/organize', methods=['POST'])
def organize_pdf():
    if 'file' not in request.files or 'ops' not in request.form:
        return jsonify({'error': 'No file or operations provided'}), 400
    
    pdf_file = request.files['file']
    ops_str = request.form['ops']
    
    try:
        ops = json.loads(ops_str)
        reader = PdfReader(pdf_file)
        writer = PdfWriter()
        
        for op in ops:
            action = op['action']
            original_index = op['originalIndex']
            
            if action == 'keep':
                page = reader.pages[original_index]
                rotation_angle = op.get('angle', page.rotation)
                
                # Check for a different rotation angle than the original
                if rotation_angle != page.rotation:
                    # PyPDF2's rotate() method is relative. We need to calculate the
                    # difference and apply it. It returns a new page object.
                    relative_rotation = rotation_angle - page.rotation
                    page = page.rotate(relative_rotation)
                
                writer.add_page(page)
            elif action == 'delete':
                pass # Skip adding the page to the writer
                
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        return send_file(
            output_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='organized.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    pdf_file = request.files['file']
    
    try:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Optimize by setting compression on streams
        writer.add_metadata(reader.metadata)
        
        for page in writer.pages:
            try:
                # Safely get the /Resources dictionary
                resources = page.get('/Resources', None)
                if resources:
                    # Safely get the /XObject dictionary from /Resources
                    xobjects = resources.get('/XObject', None)
                    if xobjects:
                        # Resolve the xobjects to their actual dictionary
                        xobjects_resolved = xobjects.get_object()
                        # Check if the resolved object is a dictionary and iterate
                        if isinstance(xobjects_resolved, dict):
                            for key, xobj in xobjects_resolved.items():
                                if '/Subtype' in xobj and xobj['/Subtype'] == '/Image':
                                    xobj.compress_contents()
            except Exception as page_error:
                # Log or ignore errors for a single page to prevent a crash
                print(f"Error processing page for compression: {page_error}")
                
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        return send_file(
            output_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='compressed.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    pdf_files = request.files.getlist('files')

    if len(pdf_files) < 2:
        return jsonify({'error': 'Please provide at least two PDF files to merge.'}), 400

    try:
        writer = PdfWriter()
        for pdf_file in pdf_files:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return send_file(
            output_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/split', methods=['POST'])
def split_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    if 'pages1' not in request.form or 'pages2' not in request.form:
        return jsonify({'error': 'Page ranges not provided'}), 400
    
    pdf_file = request.files['file']
    pages1_str = request.form['pages1']
    pages2_str = request.form['pages2']

    try:
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        pages1_indices = parse_pages(pages1_str, total_pages)
        pages2_indices = parse_pages(pages2_str, total_pages)
        
        output_files = {}

        # Split 1
        writer1 = PdfWriter()
        for index in pages1_indices:
            writer1.add_page(reader.pages[index])
        
        output1_stream = io.BytesIO()
        writer1.write(output1_stream)
        output_files['split1.pdf'] = output1_stream

        # Split 2
        writer2 = PdfWriter()
        for index in pages2_indices:
            writer2.add_page(reader.pages[index])
        
        output2_stream = io.BytesIO()
        writer2.write(output2_stream)
        output_files['split2.pdf'] = output2_stream
        
        # Create a ZIP file in-memory
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zf:
            for filename, file_stream in output_files.items():
                file_stream.seek(0)
                zf.writestr(filename, file_stream.read())
        
        zip_stream.seek(0)
        
        return send_file(
            zip_stream,
            mimetype='application/zip',
            as_attachment=True,
            download_name='split_pdfs.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files or 'type' not in request.form:
        return jsonify({'error': 'No file or conversion type provided'}), 400
    
    file = request.files['file']
    conversion_type = request.form['type']
    
    return jsonify({'error': 'Conversion is a complex feature that requires a more robust server environment with external libraries. This feature is not supported in this simple example.'}), 501

@app.route('/unlock', methods=['POST'])
def unlock_pdf():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({'error': 'No file or password provided'}), 400

    pdf_file = request.files['file']
    password = request.form['password']

    try:
        reader = PdfReader(pdf_file)
        if reader.is_encrypted:
            reader.decrypt(password)
        
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return send_file(
            output_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='unlocked.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/protect', methods=['POST'])
def protect_pdf():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({'error': 'No file or password provided'}), 400
    
    pdf_file = request.files['file']
    password = request.form['password']

    try:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        writer.encrypt(password)
        
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return send_file(
            output_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='protected.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True)
