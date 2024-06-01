import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import time
import os
import datetime
from werkzeug.utils import safe_join
import schedule


chores = ["dishes", "dishes", "cleaning kitchen",
          "trash", "living room"]

people = ["Adam", "Rishab", "Leo", "Kyle", "Leon"]

emails = ["advalade@umich.edu", "rishabj@umich.edu", "leobayer@umich.edu",
          "puffin2227@gmail.com", "wangleon@umich.edu"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE_PATH = safe_join(BASE_DIR, 'ChoresIndex.txt')
LAST_RUN_FILE_PATH = safe_join(BASE_DIR, 'last_run_time.txt')



def is_right_time():
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


def send_email(start_index):

    from_email = 'adamvalade9@gmail.com'
    password = os.environ.get('EMAIL_PASS')


    # Email server configuration
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587 


    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Upgrade the connection to secure
    server.login('adamvalade9@gmail.com', password)

    for i, person in enumerate(people):
        chore_index = (start_index + i) % len(chores)
        message_text = (f"Hello {person}, this is your weekly chore assignment. For "
           f"the week of {get_next_week_range()}, your chore is: {chores[chore_index]}.")
        
        message_text += "\n\n"
        message_text += "-Adaddy bot"
        msg = EmailMessage()
        msg['Subject'] = 'Chores'
        msg['From'] = 'Adaddy'
        msg['To'] = emails[i]
        msg.set_content(message_text)
        server.send_message(msg)
        
    server.quit()

#driver

def driver():
    if (not ran_in_last_24_hours(LAST_RUN_FILE_PATH)) and is_right_time():
        index = read_index()
        send_email(index)
        index = (index + 1) % 5
        save_run_time(LAST_RUN_FILE_PATH)
        save_index(index)

schedule.every(1).hour.do(driver)

while True:
    schedule.run_pending()
    time.sleep(1)
