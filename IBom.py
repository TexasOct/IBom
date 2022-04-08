import os

from flask import Flask, request, flash, redirect
from werkzeug.utils import secure_filename

# The dir of BOM , PCB && allowed file type
path2_IBom = "./InteractiveHtmlBom"
path2_PCB = "./fonts/PCB"
path2_BOM = "./fonts/BOM "
ALLOW_TYPE = {"kicad_pcb"}

# App settings
app = Flask('__name__', static_folder='fonts', static_url_path='')
# without secret_key it may have sth. wrong
app.secret_key = "sdkfjlqjluio23u429037907!@#!@#!@@"
app.config['uploadPath'] = path2_PCB
app.config['Bom'] = path2_BOM


# Limited file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOW_TYPE


# Generate Bom function
def Generate_Bom(filename):
    cmd = f"python3 " \
          f"{path2_IBom}/generate_interactive_bom.py " \
          f"{path2_PCB}/{filename} " \
          f"--dest-dir ../BOM " \
          f"--name-format %f"
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
        flash("No selected file", 'warning')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save upload file backup && Generate Bom
        file.save(os.path.join(app.config['uploadPath'], filename))
        Generate_Bom(filename)
        bom_Name = filename.replace('.kicad_pcb', '.html')
        # Return Bom path
        os.system(f"rm {path2_PCB}/{filename}")
        link = f"http://utexas.local/BOM/{bom_Name}"
        return f"<p>To the bom page with this <a href=\"{link}\">bottom</a> </p>"


@app.route('/BOM/<filename>', method=['post'])
def bom(filename):
    return redirect('filename')


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5000,
            debug=True)
