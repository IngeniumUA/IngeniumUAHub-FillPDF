import base64

from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.message import EmailMessage

import config_file


class Mailing:
    def __init__(self, mailReceivers, mailSubject):
        self.mailReceivers = mailReceivers
        self.mailSubject = mailSubject

    def build_service(self):
        credentials = service_account.Credentials.from_service_account_file(filename=config_file.serviceAccountFile,
                                                                            scopes=config_file.scopes)
        credentials = credentials.with_subject(config_file.emailSender)
        service = build("gmail", "v1", credentials=credentials)
        return service

    def build_message(self, mailReceiver):
        message = EmailMessage()
        message.set_content('test5')
        message["To"] = mailReceiver
        message["From"] = config_file.emailSender
        message["Subject"] = self.mailSubject

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
