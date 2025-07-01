from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_report(to_email, user_name, summary):
    sender_email = "aids22_mayur.bangera@isbmcoe.org"
    sender_password = "rtxt grez dlnh trxb"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📬 Your SPFTA Finance Summary"
    msg["From"] = sender_email
    msg["To"] = to_email

    html_content = f"""
    <html>
    <body>
        <h3>Hi {user_name},</h3>
        <p>Here’s your personal finance summary:</p>
        <pre>{summary}</pre>
        <p>Thank you for using SPFTA!</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Used to keep users logged in
@app.route('/')
def home():
    return redirect('/login')






# Load users from file
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# Save users to file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and check_password_hash(users[email], password):
            session['user'] = email
            return redirect('/dashboard')
        else:
            return '❌ Invalid credentials. Try again.'
    return render_template('login.html')






# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        users[email] = password
        save_users(users)
        return redirect('/login')
    return render_template('register.html')








@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    else:
        return redirect('/login')








@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')






from werkzeug.utils import secure_filename
import pandas as pd
import os

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read the uploaded Excel file
            try:
                df = pd.read_excel(filepath)
            except:
                return "⚠️ Error reading file. Please upload a valid Excel (.xlsx) file."

            # Save data to session (temporarily)
            session['bank_data'] = df.to_json()  # convert dataframe to JSON string

            return redirect('/analyze')

    return render_template('upload.html')













import json

import matplotlib.pyplot as plt
import uuid

@app.route('/analyze')
def analyze():
    if 'user' not in session:
        return redirect('/login')

    if 'bank_data' not in session:
        return redirect('/upload')

    df = pd.read_json(session['bank_data'])

    def categorize(description):
        desc = description.lower()
        if "uber" in desc or "ola" in desc:
            return "Transport"
        elif "pizza" in desc or "restaurant" in desc or "domino" in desc:
            return "Food"
        elif "salary" in desc or "freelance" in desc:
            return "Income"
        elif "amazon" in desc or "shopping" in desc:
            return "Shopping"
        elif "electricity" in desc or "bill" in desc:
            return "Utilities"
        else:
            return "Others"

    df['Category'] = df['Description'].apply(categorize)
    session['bank_data'] = df.to_json()

    # Generate pie chart only for expenses
    expense_df = df.copy()  # no need to filter based on Debit

    category_sum = expense_df[expense_df['Category'] != 'Income'].groupby('Category')['Amount'].sum()

    
# Temporary compatibility fix: Rename 'Type' to 'Payment Mode' if needed
    if 'Payment Mode' not in expense_df.columns and 'Type' in expense_df.columns:
        expense_df['Payment Mode'] = expense_df['Type']

    payment_sum = expense_df.groupby('Payment Mode')['Amount'].sum()


    # Create pie chart
    plt.figure(figsize=(6, 6))
    category_sum.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title('Spending Breakdown')
    plt.ylabel('')

    # Save image
    chart_filename = f'static/chart_{uuid.uuid4().hex}.png'
    plt.savefig(chart_filename)
    plt.close()



    

    # 📌 NOW ADD BAR CHART CODE HERE
    # ---- Generate Bar Chart by Category ----
    plt.figure(figsize=(8, 4))
    category_sum.plot(kind='bar', color='skyblue')
    plt.title('Total Spending by Category')
    plt.xlabel('Category')
    plt.ylabel('Amount (₹)')
    plt.tight_layout()

    # Save bar chart
    bar_chart_filename = f'static/bar_{uuid.uuid4().hex}.png'
    plt.savefig(bar_chart_filename)
    plt.close()
    
        # ---- Generate Bar Chart by Payment Mode ----
    plt.figure(figsize=(8, 4))
    payment_sum.plot(kind='bar', color='orange')
    plt.title('Spending by Payment Mode')
    plt.xlabel('Payment Mode')
    plt.ylabel('Amount (₹)')
    plt.tight_layout()

    # Save payment chart
    payment_chart_filename = f'static/payment_{uuid.uuid4().hex}.png'
    plt.savefig(payment_chart_filename)
    plt.close()
    
    session['payment_chart'] = payment_chart_filename


   
   
    
    session['chart_file'] = chart_filename
    session['bar_file'] = bar_chart_filename
    
    
    
    
    # 📨 Create summary
    summary_text = category_sum.to_string()

    # 📨 Send email
    send_email_report(session['user'], session['user'].split('@')[0], summary_text)

    

    # Convert DataFrame to HTML
    table_html = df.to_html(classes='table', index=False)



    # Convert DataFrame to HTML
    table_html = df.to_html(classes='table', index=False)
    

    return render_template(
    "analyze.html",
    table_html=df.to_html(classes='table', index=False),
    pie_chart=chart_filename,
    bar_chart=bar_chart_filename,
    payment_chart=payment_chart_filename
)


   

# ⬇️ Paste your /download_report route right here
from reportlab.pdfgen import canvas
from datetime import datetime

@app.route('/download_report')
def download_report():
    if 'user' not in session or 'bank_data' not in session:
        return redirect('/login')

    df = pd.read_json(session['bank_data'])

    filename = f"static/report_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(filename)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "📄 Personal Finance Report")
    
    # Date and User
    c.setFont("Helvetica", 10)
    c.drawString(100, 785, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 770, f"User: {session['user']}")
    
    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 740, "Recent Transactions:")

    c.setFont("Helvetica", 10)
    y = 720
    for i, row in df.head(10).iterrows():
    # ✅ This safely gets the payment info from either 'Payment Mode' or 'Type'
        payment_info = row.get('Payment Mode', row.get('Type', 'N/A'))
        category = row.get('Category', 'Uncategorized')

        line = f"{str(row['Date'])[:10]:<12} {row['Description'][:18]:<20} ₹{row['Amount']:>6}  {payment_info:<10}  {category}"
        c.drawString(100, y, line)
        y -= 15
        if y < 100:
            c.showPage()
            y = 800


    # Charts
    try:
        c.drawImage(session['chart_file'], 50, y-200, width=250, height=250)

    except:
        pass

    try:
        c.drawImage(session['bar_file'], 320, y-200, width=250, height=250)

    except:
        pass

    c.save()
    return redirect(f"/{filename}")






