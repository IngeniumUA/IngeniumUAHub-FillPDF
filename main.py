import base64
import mimetypes
import os.path
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.message import EmailMessage

import config_file


class Mailing:
    def __init__(self, mail_receivers, mail_subject, mail_content, attachments):
        self.mailReceivers = mail_receivers
        self.mailSubject = mail_subject
        self.mailContent = mail_content
        self.attachments = attachments

    def build_service(self):
        credentials = service_account.Credentials.from_service_account_file(filename=config_file.serviceAccountFile,
                                                                            scopes=config_file.scopes)
        credentials = credentials.with_subject(config_file.emailSender)
        service = build("gmail", "v1", credentials=credentials)
        return service

    def build_message(self, mail_receiver):
        message = MIMEMultipart()
        message["To"] = mail_receiver
        message["From"] = config_file.emailSender
        message["Subject"] = self.mailSubject
        mailContent = MIMEText(self.mailContent, "plain")
        message.attach(mailContent)

        for attachment in self.attachments:
            attachmentPath = attachment
            attachmentFileName = os.path.basename(attachment)
            fileType, encoding = mimetypes.guess_type(attachmentFileName)
            mainType, subType = fileType.split("/")
            attachmentData = MIMEBase(mainType, subType)

            with open(attachmentPath, "rb") as file:  # "rb" = read, binary mode (e.g. images)
                attachmentData.set_payload(file.read())
            attachmentData.add_header("Content-Disposition", "attachment", filename=attachmentFileName)
            encode_base64(attachmentData)
            #  Add the attachment to the message
            message.attach(attachmentData)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            "raw": encoded_message
        }
        return create_message

    def send_message(self):
        service = self.build_service()
        for mailReceiver in self.mailReceivers:
            message = self.build_message(mailReceiver)
            send_message = (service.users().messages().send(userId="me", body=message).execute())
            print(send_message)


"""
if __name__ == "__main__":
    mailing = Mailing(["yorben_joosen01@hotmail.com", "robbe.dehelt@student.uantwerpen.be"], "testrobbe", "varkens")
    mailing.send_message()
"""

if __name__ == "__main__":
    mailReceivers = ["yorben_joosen01@hotmail.com"]
    attachments = [r"C:\Users\yorbe\Downloads\LustrumCrick.pdf", r"C:\Users\yorbe\Downloads\Book1.xlsx"]
    mailing = Mailing(mailReceivers, "testrobbe", "varkens", attachments)
    mailing.send_message()
