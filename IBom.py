import os

from flask import Flask, request, flash, redirect
from werkzeug.utils import secure_filename


# The dir of BOM , PCB && allowed file type
path2_IBom = "./InteractiveHtmlBom"
path2_PCB = "./static/PCB"
path2_BOM = "./static/BOM "
ALLOW_TYPE = {"kicad_pcb"}


# App settings
app = Flask('__name__', static_url_path='')
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
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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
            os.system(f"rm ./static/BOM/{filename}")
            return redirect(f'BOM/{bom_Name}')

    return app.send_static_file('upload.html')


if __name__ == '__main__':
    app.run()
    