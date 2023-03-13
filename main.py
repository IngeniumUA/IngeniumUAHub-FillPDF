import base64

import googleapiclient
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.message import EmailMessage

scopes = ["https://www.googleapis.com/auth/gmail.send"]
serviceAccountfile = "gmail-credentials.json"
credentials = service_account.Credentials.from_service_account_file(filename=serviceAccountfile, scopes=scopes)
credentials = credentials.with_subject("noreply@ingeniumua.be")
service = build("gmail", "v1", credentials=credentials)

message = EmailMessage()
message.set_content('test5')
message["To"] = "s0211638@ad.ua.ac.be"
message["From"] = "noreply@ingeniumua.be"
message["Subject"] = "Test5"

encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
create_message = {
    "raw": encoded_message
}

send_message = (service.users().messages().send(userId="me", body=create_message).execute())


print(send_message)

