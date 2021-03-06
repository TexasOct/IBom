import hashlib
import os

from flask import Flask, request, flash, redirect, abort
from werkzeug.utils import secure_filename
from pathlib import Path


# The dir of BOM , PCB && allowed file type
PATH2_IBOM = './lib/InteractiveHtmlBom'
PATH2_FILE = './file'

# Allowed PCB Type
ALLOW_TYPE = {"kicad_pcb"}


# App settings
app = Flask('__name__', static_folder='fonts', static_url_path='')
# without secret_key it may get sth. wrong
app.secret_key = 'sdkfjlqjluio23u429037907!@#!@#!@@'


# Limited file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOW_TYPE


# Generate Bom function
def Generate_Bom(filename, sha):
    cmd = f"python3 " \
          f"{PATH2_IBOM}/generate_interactive_bom.py " \
          f"--no-browser " \
          f"{PATH2_FILE}/{sha}/{filename}"
    os.system(cmd)


# Path to upload
@app.route('/', methods=['GET'])
def file_path():
    return app.send_static_file('upload.html')


# Path to report
@app.route('/upload', methods=['POST'])
def Generate_file():
    if 'file' not in request.files:
        flash('No file part', 'warning')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # sha1 to keep the name different with other PCB file
        content = file.stream.read()
        shasum = hashlib.sha1()
        shasum.update(content)
        shasum = shasum.hexdigest()
        # Save upload file backup && Generate Bom
        os.makedirs(os.path.join(PATH2_FILE, shasum), exist_ok=True)
        with open(os.path.join(PATH2_FILE, shasum, filename), 'wb') as f:
            f.write(content)
        Generate_Bom(filename, shasum)
        with open('file/filelist.txt', 'a') as f:
            f.write(f'{PATH2_FILE}/{shasum}/{filename}\n')
        # Return Bom path
        return f"<p>To the bom.kicad_ page with this <a href=\"bom?id={shasum}\">bottom</a>.</p>"


@app.route('/bom', methods=['GET'])
def show_bom():
    if 'id' not in request.args:
        flash('File not exist', 'warning')
        return redirect(request.url)
    if not os.path.isdir(os.path.join(PATH2_FILE, request.args['id'])):
        abort(404)
    Path(os.path.join(PATH2_FILE, request.args['id']), 'touch').touch(exist_ok=True)
    with open(os.path.join(PATH2_FILE, request.args['id'], 'bom', 'ibom.html')) as f:
        return f.read()


# Debug option
# if __name__ == '__main__':
#     app.run(host='0.0.0.0',
#             port=5000,
#             debug=False)
