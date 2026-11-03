import os
from flask import Flask, render_template, request, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import active_tool
import auth_guard

app = Flask(__name__)
app.secret_key = "zafran_secret_key_999"
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        key = request.form.get('license_key')
        success, msg = auth_guard.verify_license_key(key, "WEB_USER_HWID")
        if success:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            error = msg
    return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        prop_type = request.form.get('prop_type')
        prop_name = request.form.get('prop_name')
        
        # Values handling based on type
        if prop_type == "VectorProperty":
            x = request.form.get('vec_x', 0)
            y = request.form.get('vec_y', 0)
            z = request.form.get('vec_z', 0)
            prop_val = f"{x},{y},{z}"
        else:
            prop_val = request.form.get('prop_val')

        if not file or file.filename == '':
            return "❌ No file uploaded!", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        with open(filepath, "rb") as f:
            content = f.read()

        new_bytes = active_tool.make_property_bytes(prop_type, prop_name, prop_val)
        if new_bytes:
            eof_marker = b"\x05\x00\x00\x00None\x00\x00"
            pos = content.rfind(eof_marker)
            base = content[:pos] if pos != -1 else content
            updated = base + new_bytes + eof_marker

            output_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(output_path, "wb") as f:
                f.write(updated)

            return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
