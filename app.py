from flask import Flask, render_template, request, redirect, url_for 
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# Get current IST time
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
formatted_time = now_ist.strftime("%B %d, %Y - %I:%M %p")

# Connect to Google Sheet
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Use the environment variable for credentials file path
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')  # Default to 'credentials.json'
    
    creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("GRVC_PDD_Submissions").sheet1

# Save form data and return row number
def save_user_data(data):
    sheet = get_google_sheet()
    row = [
        data['full_name'],
        data['email'],
        data['organization'],
        data['reason'],
        data['pdd'],
        formatted_time
    ]
    sheet.append_row(row)
    return len(sheet.get_all_values())  # last inserted row number

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/view_pdf", methods=["POST"])
def view_pdf():
    data = request.form
    row_number = save_user_data(data)
    pdf_file = f"{data['pdd']}.pdf"
    pdf_url = url_for('static', filename=f'pdfs/{pdf_file}')
    return render_template("view_pdf.html", pdf_url=pdf_url, row_number=row_number)

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    row_number = int(request.form['row_number'])
    feedback = request.form['feedback']

    sheet = get_google_sheet()
    sheet.update_cell(row_number, 7, feedback)  # Column G = 7

    return '''
    <script>
        alert("Thank you for your feedback!");
        window.location.href = "https://sites.google.com/mpensystems.com/grvcdashboard/home";  
    </script>
'''

if __name__ == "__main__":
    app.run(debug=True)
