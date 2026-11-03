import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import active_tool  # Yeh aapke asli tool ko import karega!

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        prop_type = request.form.get('prop_type')
        prop_name = request.form.get('prop_name')
        prop_val = request.form.get('prop_val')

        if not file or file.filename == '':
            return "❌ No file uploaded!", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # File read karein
        with open(filepath, "rb") as f:
            content = f.read()

        # Aapke tool ke functions use karke binary bytes banayein
        new_bytes = None
        if prop_type == "FloatProperty":
            n_size, n_hex = active_tool.name_block(prop_name)
            p_size, p_hex = active_tool.name_block("FloatProperty")
            val_hex = active_tool.hexify(active_tool.le_float(float(prop_val)))
            new_bytes = bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 04 00 00 00 00 00 00 00 00 {val_hex}")
        elif prop_type == "IntProperty":
            n_size, n_hex = active_tool.name_block(prop_name)
            p_size, p_hex = active_tool.name_block("IntProperty")
            val_hex = active_tool.hexify(active_tool.le_int(int(prop_val)))
            new_bytes = bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 04 00 00 00 00 00 00 00 00 {val_hex}")

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
