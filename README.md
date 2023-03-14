# Mailing
```
mailing = Mailing(mail_receivers=mailReceivers, mail_subject=mailSubject, mail_content=mailContent, attachments=attachments, content_type=contentType)
mailReceivers = receivers as a list of strings
mailSubject = subject of the mail as string
mailContent = content of the mail as a string (plain or html)
attachments = attachment paths as a list of strings
contentType = type of the content as string (plain or html)
mailing.send_message()
```
