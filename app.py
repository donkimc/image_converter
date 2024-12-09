import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/converted'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get the desired format
        desired_format = request.form.get('format', '').lower()
        if desired_format not in app.config['ALLOWED_EXTENSIONS']:
            return "Invalid format selected", 400

        # Convert the image
        base_filename = os.path.splitext(filename)[0]
        converted_filename = "{}.{}".format(base_filename, desired_format)
        converted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)

        try:
            with Image.open(file_path) as img:
                img.convert('RGB').save(converted_file_path, desired_format.upper())
        except Exception as e:
            return "Failed to convert image: {}".format(str(e)), 500

        return render_template('result.html', original=file_path, converted=converted_file_path)

    return "File not allowed", 400

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
