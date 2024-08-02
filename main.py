import pandas as pd
from post_email import post_email
from flask import Flask, request, send_from_directory, render_template_string, session
import os

def load_df(url):
    usecols = ["Name","Email","Completed Latest Work?"]
    df = pd.read_csv(url,usecols=usecols)
    return df

def query_broad(df, file, uurl):
    email_counter = 0
    for index, row in df.iterrows():
        post_email(
            recipient=row["Email"],
            name=row["Name"],
            filedir=file,
            formlink=uurl
        )
        email_counter += 1
    return f"{email_counter} emails sent"
def query_specific(df, file, uurl):
    email_counter = 0
    for index, row in df.iterrows():
        if row["Completed Latest Work?"] == "Y":
            post_email(
                recipient=row["Email"],
                name=row["Name"],
                filedir=file,
                formlink=uurl
            )
            email_counter += 1
        else:
            continue
    return f"{email_counter} emails sent"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 32 * 1024 * 1024  # 16 megabytes

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.secret_key = 'very secret key'

@app.route('/')
def index():
    # Return HTML content that includes a form with a file input, a text input for URL, and a submit button
    return render_template_string('''
        <!doctype html>
        <title>학습지 와 문제 전송</title>
        <h1>Upload a file and submit a URL</h1>
        <form method="post" action="/upload" enctype="multipart/form-data">
          <input type="file" name="file"><br><br>
          <input type="text" name="url" placeholder="Enter URL here"><br><br>
          <input type="submit" value="Upload">
        </form>
        ''')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Retrieve the filename from the uploaded file
    file = request.files['file']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    # Retrieve the user-submitted URL from the form
    user_url = request.form.get('url', 'No URL provided')
    session['filedir'] = filename
    session['user_url'] = user_url

    # Return HTML content displaying the filename, the user URL, and include a button to send an email
    return render_template_string(f'''
        <!doctype html>
        <title>Upload Results</title>
        <h1>Upload Results</h1>
        Uploaded File Name: {filename}<br>
        Submitted URL: {user_url}<br><br>
        <form method="post" action="/specific-email">
          <input type="submit" value="지정된 수신자에게 보내기">
        </form>
        <form method="post" action="/broad-email">
          <input type="submit" value="모두에게 보내기">
        </form>
        ''')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serves the requested file from the upload directory using the filename
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/specific-email', methods=['POST'])
def specific_email():
    filepath = session.get('filedir', 'No file uploaded')
    userurl = session.get('user_url', 'No URL provided')
    SHEET_ID = "12cKj6sS3JfZjd89BxivhHOYlwRFdhffTc-pMycTLDbA"
    SHEET_NAME = "Class_Roster"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    emnum = query_specific(load_df(URL), filepath, userurl)
    return f'''
    <!doctype html>
    <title>Email Sent</title>
    <h1> Number of email(s) sent: {emnum} </h1>
    All email(s) have been sent successfully!
    '''
@app.route('/broad-email', methods=['POST'])
def broad_email():
    filepath = session.get('filedir', 'No file uploaded')
    userurl = session.get('user_url', 'No URL provided')
    SHEET_ID = "12cKj6sS3JfZjd89BxivhHOYlwRFdhffTc-pMycTLDbA"
    SHEET_NAME = "Class_Roster"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    emnum = query_broad(load_df(URL), filepath, userurl)
    return f'''
    <!doctype html>
    <title>Email Sent</title>
    <h1> Number of email(s) sent: {emnum} </h1>
    All email(s) have been sent successfully!
    '''

if __name__ == '__main__':
    app.run(debug=True, port=4000)
