import os
import json
import hashlib
import qrcode
from flask import Flask, render_template, request, jsonify
from web3 import Web3
from fpdf import FPDF
from datetime import datetime
from utilis import detect_tampering
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "smartcert_super_secret_key" # Idhu session-ku romba mukkiyam

# --- EMAIL CONFIGURATION ---
SENDER_EMAIL = "smartcert101@gmail.com"  # Unga Gmail ID
SENDER_PASS = "utdtvuhztrmuaoqp"    # Neenga generate panna 16-digit App Password

# Analytics track panna variables
total_issued = 0
total_verified = 0
tamper_alerts = 0

# Folders Setup
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
QR_FOLDER = 'static/qrcodes'
PDF_FOLDER = 'static/issued_certs'

for folder in [UPLOAD_FOLDER, RESULT_FOLDER, QR_FOLDER, PDF_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 1. Blockchain Connection (Ganache)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Verification History store panna oru empty list (NEW)
verify_history = []

# deployed_info.json-la irundhu details edukirom
try:
    with open("deployed_info.json", "r") as f:
        data = json.load(f)
        contract_address = data['address']
        abi = data['abi']
    contract = w3.eth.contract(address=contract_address, abi=abi)
except FileNotFoundError:
    print("Error: deployed_info.json file-ah kaanom! Modhala deploy.py run pannunga.")

def generate_pdf_certificate(name, s_id, email, dept, year, p_hash):

    """Details sethu Professional PDF generate pannum"""
    pdf = FPDF()
    pdf.add_page()
    
    # Border & Design (Olive Green - Neenga ketta theme)
    pdf.set_draw_color(85, 107, 47) 
    pdf.rect(5, 5, 200, 287)
    
    # Title
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(200, 40, "OFFICIAL UNIVERSITY CERTIFICATE", ln=True, align='C')
    
    # Student Info
    pdf.set_font("Arial", size=14)
    pdf.ln(10)
    pdf.cell(200, 10, f"Student Name: {name}", ln=True)
    pdf.cell(200, 10, f"Student ID: {s_id}", ln=True)
    pdf.cell(200, 10, f"Email: {email}", ln=True)
    pdf.cell(200, 10, f"Department: {dept}", ln=True)
    pdf.cell(200, 10, f"Passing Year: {year}", ln=True)
    pdf.cell(200, 10, f"Issued Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    
    # Blockchain Hash
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, f"Blockchain Digital Signature (Hash): {p_hash}")
    
    # QR Code logic (Modified to Link for direct verification if needed)
    qr_data = f"ID:{s_id}\nHash:{p_hash[:20]}\nVerified: Blockchain"
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join(QR_FOLDER, f"{s_id}.png")
    qr_img.save(qr_path)
    pdf.image(qr_path, x=150, y=55, w=40) # QR position
    
    pdf_path = os.path.join(PDF_FOLDER, f"{s_id}.pdf")
    pdf.output(pdf_path)
    return pdf_path


def send_email_notification(student_email, student_name, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = 'Blockchain Certificate Issued! 🎓'
    msg['From'] = SENDER_EMAIL
    msg['To'] = student_email
    
    msg.set_content(f"""Hi {student_name},

Your digital certificate has been successfully signed and secured on the Blockchain.
Please find your attached certificate for your records.

This is an automated secure notification.
Best regards,
Blockchain CertiChain Team""")

    # PDF-ah attach panrom
    try:
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(
                file_data, 
                maintype='application', 
                subtype='pdf', 
                filename=f"{student_name}_Certificate.pdf"
            )

        # SSL (Port 465) vazhiya send panrom
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
            print(f">>> ✅ Email sent successfully to {student_email}")
            
    except Exception as e:
        print(f">>> ❌ Email Error: {e}")


@app.route('/')
def index():
    return render_template('index.html')

ADMIN_KEY = "keerthi98##" 
ADMIN_USER = "keerthi"# Inga dhaan neenga password set pannanum

# --- LOGIN ROUTE (NEW) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        passw = request.form.get('password')
        
        # Inga namma ADMIN_KEY-ai password-ah use panrom
        if user == ADMIN_USER and passw == ADMIN_KEY:
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
        else:
            error = "Invalid Username or Admin Key!"
            
    return render_template('login.html', error=error)

# --- UPDATED ADMIN ROUTE ---
@app.route('/admin')
def admin_page():
    # Login pannala-na admin page-kulla poga mudiyaathu
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

# --- LOGOUT ROUTE ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


# History details-ah Admin Page table-ku anuppa (NEW)
@app.route('/get_history')
def get_history():
    return jsonify(verify_history)


@app.route('/get_analytics')
def get_analytics():
    return jsonify({
        "issued": total_issued,
        "verified": total_verified,
        "alerts": tamper_alerts
    })

# --- ISSUE ROUTE ---
@app.route('/issue', methods=['POST'])
def issue():

    global total_issued
    try:
        provided_pass = request.form.get('admin_pass')
        if provided_pass != ADMIN_KEY:
            return jsonify({"status": "Error", "message": "Wrong Admin Access Key!"})


        # Form values-ah sariyaana names-la edukkurom
        name = request.form.get('name')
        s_id = request.form.get('id')
        email = request.form.get('email')
        dept = request.form.get('dept')
        year = request.form['year']
        file = request.files.get('image')

        # VALIDATION: Ethavathu miss aana stop pannidum
        if not all([name, s_id, email, dept, year, file]):
            return jsonify({"status": "Error", "message": "All fields (including Student ID) are required!"})

        # --- BLOCKCHAIN LOGIC ---
        img_path = os.path.join(UPLOAD_FOLDER, f"{s_id}.png")
        file.save(img_path)
        with open(img_path, "rb") as f:
            p_hash = hashlib.sha256(f.read()).hexdigest()

        admin = w3.eth.accounts[0]
        tx_hash = contract.functions.initiateCertificate(
            s_id, name, email, dept, str(year), p_hash
        ).transact({'from': admin})
        w3.eth.wait_for_transaction_receipt(tx_hash)

        total_issued += 1
        
        # PDF matrum Email Notification
       
        pdf_file = generate_pdf_certificate(name, s_id, email, dept, year, p_hash)
        
        pdf_url = f"/static/issued_certs/{s_id}.pdf"

        try:

            send_email_notification(email, name, pdf_file)
            print("Email sent successfully!")

        except:
            print("Email failed but blockchain stored.")

        
       
        # PDF link-ai response-udan anuppugirom
        return jsonify({
            "status": "Success", 
            "message": "Certificate Secured & Email Sent!",
            "pdf_url": pdf_url
        }) 
    
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})
    


# --- VERIFY ROUTE ---
@app.route('/verify', methods=['POST'])
def verify():
    global total_verified, tamper_alerts
    try:
        s_id = request.form['id']
        file = request.files['image']
        
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_verify_{s_id}.png")
        file.save(temp_path)
        
        with open(temp_path, "rb") as f:
            input_hash = hashlib.sha256(f.read()).hexdigest()
        
        is_valid, msg = contract.functions.verifyIntegrity(s_id, input_hash).call()

        total_verified += 1
        
        # History-la entry podurathu (NEW)
        status_label = "Genuine" if is_valid else "Tampered/Fake"

        if not is_valid:
            tamper_alerts += 1 

        verify_history.append({
            "id": s_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status_label
        })
        
        if is_valid:
            details = contract.functions.getCertificateDetails(s_id).call()
            return jsonify({
                "status": "Genuine", 
                "message": "✅ Verification Successful: Authentic Document!",
                "data": {"name": details[0], "dept": details[2], "year": details[3]}
            })
        else:
            original_img = os.path.join(UPLOAD_FOLDER, f"{s_id}.png")
            if os.path.exists(original_img):
                score, result_path = detect_tampering(original_img, temp_path)
                return jsonify({
                    "status": "Fake", 
                    "message": "❌ TAMPERING DETECTED: Pixel manipulation found!",
                    "score": round(score, 4),
                    "report": "/" + result_path
                })
            else:
                return jsonify({"status": "Fake", "message": "No original record found for this ID to compare."})
            

                
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)


