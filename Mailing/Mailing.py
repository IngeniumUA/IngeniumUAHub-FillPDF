import base64
from base64 import urlsafe_b64encode as base64_urlsafe_encode
from mimetypes import guess_type as mimetypes_guess_type
from os import path as os_path
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleHttpError


class MailingClass:
    """
    Implements the Gmail API to send mails
    """

    def __init__(
        self,
        mail_receivers: list[str],
        mail_subject: str,
        mail_content: str,
        mail_sender: str,
        service_file_path: str,
        attachments: list[str | bytes] = None,
        content_type: str = "plain",
    ) -> None:
        """
        :param mail_receivers: Receivers
        :param mail_subject: Subject of the mail
        :param mail_content: Content of the mail options: html and plain
        :param mail_sender: Sender of the mail
        :param service_file_path: Path to the service account json
        :param attachments: Attachment paths
        :param content_type: Type of the content options: string with html code in or normal string
        """
        if attachments is None:
            attachments = []

        self.mailReceivers = mail_receivers
        self.mailSubject = mail_subject
        self.mailContent = mail_content
        self.attachments = attachments
        self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
        self.mailSender = mail_sender

        if not os_path.exists(service_file_path):
            raise Exception("Service account json path does not exist")

        self.serviceFilePath = service_file_path

        if content_type != "plain" and content_type != "html":
            raise Exception("Wrong content type")

        self.contentType = content_type
        self.service = self._build_service()

    def _build_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.serviceFilePath, scopes=self.scopes, subject=self.mailSender
        )
        service = build("gmail", "v1", credentials=credentials)
        return service

    def _build_message(self, mail_receiver: str) -> dict:
        """
        :param mail_receiver: Receiver of the mail
        :return: Returns the body
        """
        # MIME stands for Multipurpose Internet Mail Extensions and is an internet standard that is used to support the transfer of single or multiple text
        # and non-text attachments
        message = MIMEMultipart()  # Create an empty MIMEMultipart message
        message["To"] = mail_receiver
        message["From"] = self.mailSender
        message["Subject"] = self.mailSubject
        mailContent = MIMEText(self.mailContent, self.contentType)
        message.attach(mailContent)

        # Loop over the list of attachments
        for attachment in self.attachments:
            if not isinstance(attachment, (str, bytes)):
                raise Exception("Attachment is not a string or bytes.")

            if isinstance(attachment, str):
                if not os_path.exists(attachment):
                    raise Exception("Service account json path does not exist")
                attachmentPath = (
                    attachment  # Save the path, because this is needed later on
                )
                attachmentFileName = os_path.basename(attachment)
                fileType, encoding = mimetypes_guess_type(attachmentFileName)
                mainType, subType = fileType.split("/")
                attachmentData = MIMEBase(mainType, subType)

                # Open the attachment, read it and write its content into attachmentData
                with open(
                    attachmentPath, "rb"
                ) as file:  # "rb" = read, binary mode (e.g. images)
                    attachmentData.set_payload(file.read())
                # Add header to attachmentData so that the name of the attachment stays
                attachmentData.add_header(
                    "Content-Disposition", "attachment", filename=attachmentFileName
                )
                encode_base64(attachmentData)  # Encode the attachmentData
            else:
                attachmentData = attachment
            message.attach(attachmentData)

        encoded_message = message.as_string()
        create_message = {"raw": encoded_message}
        return create_message

    def send_message(self) -> None:
        for mailReceiver in self.mailReceivers:
            message = self._build_message(mailReceiver)
            try:
                self.service.users().messages().send(
                    userId="me", body=message
                ).execute()
            except GoogleHttpError as error:
                raise Exception(error.reason)
