import base64
import mimetypes
import os.path
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build


class MailingClass:
    """
    Implements the Gmail API to send mails
    """
    # Constructor
    def __init__(self, mail_receivers, mail_subject, mail_content, mail_sender, service_file_path, attachments=None, content_type="plain"):
        """
        :param mail_receivers: Receivers as a list of strings
        :param mail_subject: Subject of the mail as a string
        :param mail_content: Content of the mail as a string, options: html and plain
        :param mail_sender: Sender of the mail
        :param service_file_path: Path to the service account json
        :param attachments: Attachment paths as a list of strings
        :param content_type: Type of the content as string, options: string with html code in or normal string
        """
        if attachments is None:
            attachments = []
        self.mailReceivers = mail_receivers
        self.mailSubject = mail_subject
        self.mailContent = mail_content
        self.attachments = attachments
        self.contentType = content_type
        self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
        self.mailSender = mail_sender
        if os.path.exists(service_file_path):
            self.serviceFilePath = service_file_path
        else:
            raise Exception("Service account json path does not exist")

    # Build the service that connects to Gmail API
    def _build_service(self):
        # Create credentials form the service account file
        credentials = service_account.Credentials.from_service_account_file(filename=self.serviceFilePath, scopes=self.scopes)
        # Link the correct email address to the credentials
        credentials = credentials.with_subject(self.mailSender)
        # Build the service
        service = build("gmail", "v1", credentials=credentials)
        return service

    #  Builds the contents of the mail
    def _build_message(self, mail_receiver):
        # MIME stands for Multipurpose Internet Mail Extensions and is an internet standard that is used to support the transfer of single or multiple text
        # and non-text attachments

        message = MIMEMultipart()  # Create an empty MIMEMultipart message
        message["To"] = mail_receiver  # Set the receivers
        message["From"] = self.mailSender  # Add the sender
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
        service = self._build_service()
        for mailReceiver in self.mailReceivers:
            message = self._build_message(mailReceiver)
            service.users().messages().send(userId="me", body=message).execute()
