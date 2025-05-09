import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

class ConnectMail:
    """
        This class is connection to a GMAIL server for sending mails regarding the oct news updater.
        You can choose a reference mail, and
    """
    def __init__(self,reference_mail, info=False):
        # Loading the secret information from .env file
        load_dotenv()
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.ref_mail = reference_mail
        self.info = info
        try:
            self.connection = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.connection.login(self.email_address, self.email_password)
            if self.info:
                self.send_mail("LogIn", "App is connected.")
        except Exception as err:
            print(f"Could not connect to mail-server.\n{err}")


    def send_mail(self,subject, content):

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'OCT-NEWS updater'
        msg['To'] = self.ref_mail
        msg.set_content(f"Your email-client is not support html.")
        msg.add_alternative(content, subtype='html')
        try:
            self.connection.send_message(msg)
            print("Send mail with html content.")
        except Exception as err:
            print(f"Could not send mail.\n{err}")

    def send_mail_text(self,subject, content):

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'OCT-NEWS updater'
        msg['To'] = self.ref_mail
        msg.set_content(content)
        try:
            self.connection.send_message(msg)
            print("Send mail with text.")
        except Exception as err:
            print(f"Could not send mail.\n{err}")

    def close(self):
        if self.info:
            self.send_mail("LogOut", "App is disconnected.")
        self.connection.quit()


if __name__=="__main__":

    con_obj = ConnectMail('test@test.com')

    con_obj.send_mail("Test Mail",  "Das ist der Test Inhalt.")

    con_obj.close()