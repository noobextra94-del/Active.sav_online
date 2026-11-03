import os
import uuid
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

    msg = None
    file_uploaded_name = session.get('file_original_name', None)

    if request.method == 'POST':
        action = request.form.get('action')
        
        # 1. Agar user ne nayi file di hai toh save karein
        file = request.files.get('file')
        if file and file.filename != '':
            original_name = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + original_name
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # Session mein save kar lo taake bar bar file na maange
            session['file_path'] = filepath
            session['file_original_name'] = original_name
            file_uploaded_name = original_name
            msg = f"📁 '{original_name}' successfully loaded! Ab properties add karein."

        current_file = session.get('file_path')

        # 2. Agar property save ya download karni hai
        if action in ['save_more', 'download']:
            if not current_file or not os.path.exists(current_file):
                return render_template('index.html', error="❌ Pehle upar se Active.sav file select kar ke upload karein!")

            prop_type = request.form.get('prop_type')
            prop_name = request.form.get('prop_name')
            
            if prop_type == "VectorProperty":
                x = request.form.get('vec_x', 0)
                y = request.form.get('vec_y', 0)
                z = request.form.get('vec_z', 0)
                prop_val = f"{x},{y},{z}"
            else:
                prop_val = request.form.get('prop_val')

            # Binary bytes generate karke inject karo
            new_bytes = active_tool.make_property_bytes(prop_type, prop_name, prop_val)
            if new_bytes:
                active_tool.inject_to_file(current_file, new_bytes)
                msg = f"✅ Property '{prop_name}' ({prop_type}) add ho gayi! File memory mein save hai, mazeed properties daal sakte hain."

            if action == 'download':
                return send_file(current_file, as_attachment=True, download_name="Active.sav")

    return render_template('index.html', message=msg, file_loaded=file_uploaded_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
