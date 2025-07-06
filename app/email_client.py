import imaplib
import email
from email.header import decode_header
from datetime import datetime

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def fetch_emails(email_user, email_pass, imap_host):
    print(f"🔐 Connecting to {imap_host} as {email_user}")
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(email_user, email_pass)
    mail.select("inbox")

    # Search for unread emails only
    status, messages = mail.search(None, "UNSEEN")

    if status != "OK":
        raise Exception("Could not fetch emails")

    email_list = []

    for num in messages[0].split():
        res, msg_data = mail.fetch(num, "(RFC822)")
        if res != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

        # Decode sender
        from_ = msg.get("From")

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
        else:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="ignore")

        email_list.append({
            "sender": from_,
            "subject": subject.strip(),
            "body": body.strip(),
            "status": "unread",
            "date": datetime.now()
        })

    mail.logout()
    return email_list

