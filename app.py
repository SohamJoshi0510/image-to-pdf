from flask import Flask, render_template, request, redirect, url_for, session, send_file
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Route to handle the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'images' not in session:
        session['images'] = []

    if request.method == 'POST':
        # Handle file uploads
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                session['images'].append(file.filename)
        session.modified = True

    return render_template('index.html', images=session['images'])

# Route to generate PDF
@app.route('/generate_pdf')
def generate_pdf():
    images = session.get('images', [])
    
    # Debug: Check if images exist in the session
    if not images:
        print("No images found in session for PDF generation.")
        return redirect(url_for('index'))
    
    # Open and convert images to PDF
    image_list = [Image.open(os.path.join(app.config['UPLOAD_FOLDER'], img)).convert('RGB') for img in images]
    
    # Define the output PDF path
    output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')

    # Save the images as a PDF
    try:
        image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
        print(f"PDF generated successfully at {output_pdf}.")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return redirect(url_for('index'))

    # Clear the session after successful PDF generation
    session['images'] = []

    # Redirect to the generated PDF for download
    return redirect(f'/static/uploads/output.pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)