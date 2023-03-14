import base64
import mimetypes
import os.path
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build

from MailingIngeniumUAHub import config_file


class MailingClass:
    # Constructor
    def __init__(self, mail_receivers, mail_subject, mail_content, attachments, content_type):
        self.mailReceivers = mail_receivers
        self.mailSubject = mail_subject
        self.mailContent = mail_content
        self.attachments = attachments
        self.contentType = content_type

    # Build the service that connects to Gmail API
    def build_service(self):
        # Create credentials form the service account file
        credentials = service_account.Credentials.from_service_account_file(filename=config_file.serviceAccountFile,
                                                                            scopes=config_file.scopes)
        # Link the correct email address to the credentials
        credentials = credentials.with_subject(config_file.emailSender)
        # Build the service
        service = build("gmail", "v1", credentials=credentials)
        return service

    #  Builds the contents of the mail
    def build_message(self, mail_receiver):
        # MIME stands for Multipurpose Internet Mail Extensions and is an internet standard that is used to support the transfer of single or multiple text
        # and non-text attachments

        message = MIMEMultipart()  # Create an empty MIMEMultipart message
        message["To"] = mail_receiver  # Set the receivers
        message["From"] = config_file.emailSender  # Add the sender
        message["Subject"] = self.mailSubject  # Set the subject
        mailContent = MIMEText(self.mailContent, self.contentType)  # Make MIMEText of the content of the mail and its type (html and plain)
        message.attach(mailContent)  # Add the content to the message

        # Loop over the list of attachments
        for attachment in self.attachments:
            attachmentPath = attachment  # Save the path, because this is needed later on
            attachmentFileName = os.path.basename(attachment)  # Get the filename from the attachment
            fileType, encoding = mimetypes.guess_type(attachmentFileName)  # Get the filetype and encoding from the attachment name
            mainType, subType = fileType.split("/")  # Get the main and subtype from the filetype
            attachmentData = MIMEBase(mainType, subType)

            # Open the attachment, read it and write its content into attachmentData
            with open(attachmentPath, "rb") as file:  # "rb" = read, binary mode (e.g. images)
                attachmentData.set_payload(file.read())
            # Add header to attachmentData so that the name of the attachment stays
            attachmentData.add_header("Content-Disposition", "attachment", filename=attachmentFileName)
            encode_base64(attachmentData)  # Encode the attachmentData
            message.attach(attachmentData)  # Add the attachmentData to the message

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            "raw": encoded_message
        }
        return create_message

    def send_message(self):
        service = self.build_service()
        for mailReceiver in self.mailReceivers:
            message = self.build_message(mailReceiver)
            service.users().messages().send(userId="me", body=message).execute()
