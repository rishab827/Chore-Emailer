from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import time
import os
import datetime
from werkzeug.utils import safe_join

secretpass = os.getenv('EMAIL_PASSWORD')

app = Flask(__name__)

chores = []

people = []

emails = []

#index_file_path = '/Users/rishab/Desktop/emailProject/ChoresIndex.txt'
#filename = '/Users/rishab/Desktop/emailProject/last_run_time.txt'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOP_FILE_PATH = safe_join(BASE_DIR, 'stop_state.txt')
INDEX_FILE_PATH = safe_join(BASE_DIR, 'ChoresIndex.txt')
LAST_RUN_FILE_PATH = safe_join(BASE_DIR, 'last_run_time.txt')

def is_right_time():
    return True  #for testing purposes
    now = datetime.datetime.now()
    if now.weekday() == 6:
        return True
    else:
        return False

def save_run_time(LAST_RUN_FILE_PATH):
    with open(LAST_RUN_FILE_PATH, 'w') as file:
        file.write(datetime.datetime.now().isoformat())
        
def ran_in_last_24_hours(LAST_RUN_FILE_PATH):
    if not os.path.exists(LAST_RUN_FILE_PATH):
        return False

    with open(LAST_RUN_FILE_PATH, 'r') as file:
        last_run_time_str = file.read().strip()
        if not last_run_time_str:  # Check if the string is empty
            return False

    try:
        last_run_time = datetime.datetime.strptime(last_run_time_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return False  # If the format is incorrect, assume the script hasn't run

    return (datetime.datetime.now() - last_run_time) < datetime.timedelta(hours=24)
                 

def read_index():
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as file:
            return int(file.read().strip())
    return 0

# Function to save the index to the file
def save_index(index):
    with open(INDEX_FILE_PATH, 'w') as file:
        file.write(str(index))

def get_next_week_range():
    today = datetime.date.today()
    days_to_next_monday = 1 if today.weekday() == 6 else (7 - today.weekday())
    next_monday = today + datetime.timedelta(days=days_to_next_monday)
    next_sunday = next_monday + datetime.timedelta(days=6)
    
    # Format dates to 'MM-DD' format
    next_monday_str = next_monday.strftime("%m-%d")
    next_sunday_str = next_sunday.strftime("%m-%d")

    return f"{next_monday_str} - {next_sunday_str}"

# Consider importing "safe_join" from Flask's "werkzeug.utils" for filepath concatenation
# Modify the file paths to make them more dynamic and secure
# For example, you could create a base directory variable:


def check_stop_state():
    # Check the stop state file to see if the stop flag has been set
    if os.path.exists(STOP_FILE_PATH):
        with open(STOP_FILE_PATH, 'r') as file:
            return file.read().strip().lower() == 'stop'
    return False

def set_stop_state():
    # Set the stop flag in the file
    with open(STOP_FILE_PATH, 'w') as file:
        file.write('stop')

def send_email(people, emails, chores, start_index):
    print("RUNNING")
    global email_sending_status
    from_email = 'rishab.jayaraman@gmail.com'
    password = secretpass

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, password)
    
    for i, person in enumerate(people):
        print("LOOPING")
        chore_index = (start_index + i) % len(chores)
        message_text = (f"Hello {person}, this is your weekly chore assignment. For "
           f"the week of {get_next_week_range()}, your chore is: {chores[chore_index]}.")
        
        message_text += "\n\n- Chore Emailer"
        msg = EmailMessage()
        msg['Subject'] = 'Chores'
        msg['From'] = 'Email Bot'
        msg['To'] = emails[i]
        msg.set_content(message_text)

        # Update status before each email is sent
        email_sending_status = f"Sending emails..."
        server.send_message(msg)
        print("FINITO")
        
    email_sending_status = "Idle"
    server.quit()

@app.route('/status')
def email_status():
    new_status = email_sending_status
    return new_status

@app.route('/stop', methods=['POST'])
def stop_emails():
    global email_sending_status  # Reference the global variable
    set_stop_state()
    email_sending_status = "Idle"  # Reset the status message
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    print("Main Running")
    if request.method == 'POST':
        print("Post Running")
        global chores, emails, email_sending_status
        chores = request.form.getlist('chores[]')
        emails = request.form.getlist('emails[]')
        people = request.form.getlist('people[]')
        print(people)
        print(emails)
        print(chores)

        if (not ran_in_last_24_hours(LAST_RUN_FILE_PATH)) and is_right_time() and not check_stop_state():
            index = read_index()
            print("Send Email Running")
            send_email(people, emails, chores, index)
            index = (index + 1) % len(chores)
            save_run_time(LAST_RUN_FILE_PATH)
            save_index(index)
            email_sending_status = "Email Sending is Active!"
        else:
            print("Not Sending")
            if ran_in_last_24_hours(LAST_RUN_FILE_PATH):
                email_sending_status = "24"
            if not is_right_time():
                email_sending_status = "not right time"
            if check_stop_state():
                email_sending_status = "stop state"

            #email_sending_status = "Emails have not been sent. Either it's not the right time, or the stop flag is set, or it's not enabled."

        return redirect(url_for('index'))

    return render_template('form.html')

@app.route('/submit-form', methods=['POST'])
def handle_form():
    print("RANNNNN2")
    emails = request.form.getlist('emails[]')
    chores = request.form.getlist('chores[]')
    # Process the data as needed
    return render_template('form.html')


@app.route('/success')
def success():
    return 'Emails have been sent successfully!'

if __name__ == '__main__':
    app.run(debug=True)