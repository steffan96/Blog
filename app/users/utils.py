from logging import shutdown
from PIL import Image
import os
from flask import current_app, url_for, abort, request
import secrets

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_name)
    small_picture_path = os.path.join(current_app.root_path, 'static/small_profile_pics', picture_name)
    
    small_output_size = (35,31)
    i = Image.open(form_picture)
    i.thumbnail(small_output_size)
    i.save(small_picture_path)

    output_size = (125,111)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_name


def send_confirmation_mail(user):
    USER_EMAIL = os.environ.get("EMAIL_USER")
    USER_PASSWORD = os.environ.get("EMAIL_PASS")

    msg = MIMEMultipart()
    token = user.generate_confirmation_token()
    text = f'''Hello {user.username}, 
Welcome to Pisite Gluposti!
To confirm your account please click on the following link:
{url_for('users.confirm', token=token, _external=True)}
Please do not respond on this email.
'''
   
     


    msg["from"] = USER_EMAIL
    msg["to"] = user.email
    msg["subject"] = 'Please confirm your account'

    msg.attach(MIMEText(text, 'plain'))

    

    try:
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()
        server.login(USER_EMAIL, USER_PASSWORD)
        server.sendmail(USER_EMAIL, msg["to"], msg.as_string())

        
    except Exception as e:
        pass

    finally:
        server.quit()




def reset_password_mail(user):
    USER_EMAIL = os.environ.get("EMAIL_USER")
    USER_PASSWORD = os.environ.get("EMAIL_PASS")
    username = user.username
    msg = MIMEMultipart()
    token = user.generate_confirmation_token()
    text = f'''Hello {user.username}, 
To reset your password please click on the following link:
{url_for('users.reset_password', username=username, token=token, _external=True)}
Please do not respond on this email.
'''
   
     


    msg["from"] = USER_EMAIL
    msg["to"] = user.email
    msg["subject"] = 'Reset Your Password'

    msg.attach(MIMEText(text, 'plain'))

    

    try:
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()
        server.login(USER_EMAIL, USER_PASSWORD)
        server.sendmail(USER_EMAIL, msg["to"], msg.as_string())

        
    except Exception as e:
        pass

    finally:
        server.quit()


