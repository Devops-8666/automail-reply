from flask import Flask, render_template, request, redirect, session,url_for,flash
from app.email_client import fetch_emails
from worker.ai_reply import generate_email_from_prompt
from app.database import (
    save_emails,
    get_emails,
    get_email_by_id,
    update_email_status,
    update_reply_only,
    clear_emails_for_user,
)
import pika
import json
from bson.objectid import ObjectId
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 🐇 Send to RabbitMQ
def send_to_queue(email_id, reply_text):
    try:
        #rabbit_host = os.getenv("RABBITMQ_HOST", "localhost")  # fallback for dev
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
        CLOUD_AMQP_URL = os.getenv("CLOUD_AMQP_URL")
        print(f"[DEBUG] CLOUD_AMQP_URL = {CLOUD_AMQP_URL}")
        
        if not CLOUD_AMQP_URL:  
            raise ValueError("CLOUD_AMQP_URL not set in environment")

        params = pika.URLParameters(CLOUD_AMQP_URL)
        connection = pika.BlockingConnection(params)
        
        channel = connection.channel()
        channel.queue_declare(queue="reply_queue")
        message = json.dumps({"id": str(email_id), "text": reply_text})
        channel.basic_publish(exchange="", routing_key="reply_queue", body=message)
        connection.close()
        print(f"[✓] Queued email {email_id} with reply: {reply_text[:30]}...")
    except Exception as e:
        print(f"[✗] Failed to queue message: {e}")

# 📤 Send reply email via SMTP
def send_email_reply(user_email, app_password, to_address, subject, body):
    msg = MIMEText(body)
    msg["From"] = user_email
    msg["To"] = to_address
    msg["Subject"] = "Re: " + subject

    try:
        # Gmail: smtp.gmail.com (port 587)
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()
        smtp_server.login(user_email, app_password)
        smtp_server.send_message(msg)
        smtp_server.quit()
        print(f"[📤] Sent reply to {to_address}")
    except Exception as e:
        print(f"[✗] Failed to send email: {e}")
#Send reply email via SMTP,used for /compose only (✅ has BCC)
def send_email_with_bcc(user_email, app_password, to_address, subject, body):
    msg = MIMEText(body)
    msg["From"] = user_email
    msg["To"] = to_address
    msg["Subject"] = subject
    msg["Bcc"] = user_email  # ✅ Only here

    try:
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()
        smtp_server.login(user_email, app_password)
        smtp_server.send_message(msg)
        smtp_server.quit()
        print(f"[📤] Sent composed email to {to_address} (BCC to self)")
    except Exception as e:
        print(f"[✗] Failed to send email: {e}")


# 🔐 Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["email"] = request.form["email"]
        session["password"] = request.form["password"]
        session["imap_host"] = request.form["imap_host"]

        try:
            print(f"🔐 Connecting to {session['imap_host']} as {session['email']}")
            emails = fetch_emails(session["email"], session["password"], session["imap_host"])
            print(f"📥 {len(emails)} emails fetched from IMAP")

            clear_emails_for_user(session["email"])
            save_emails(emails, session["email"])

            # 🐇 Queue all for AI replies
            for email in emails:
                send_to_queue(email["_id"], email["body"])

            return redirect("/inbox")
        except Exception as e:
            return f"Login failed: {str(e)}"

    return render_template("login.html")

# 📥 Inbox view
@app.route("/inbox")
def inbox():
    if "email" not in session:
        return redirect("/")

    emails = get_emails(session["email"])

    unread_emails = sorted(
        [e for e in emails if e.get("status", "unread") == "unread"],
        key=lambda x: x.get("date", str(x["_id"])),
        reverse=True
    )

    return render_template(
        "inbox.html",
        emails=unread_emails,
        unread=sum(1 for e in emails if e.get("status", "unread") == "unread"),
        read=sum(1 for e in emails if e.get("status") == "replied"),
        skipped=sum(1 for e in emails if e.get("status") == "skipped"),
        total=len(emails)
    )

# ✏️ Edit reply
# ✏ Edit reply
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    email = get_email_by_id(id)
    print("DEBUG Email object:", email)
    print("REPLY FIELD:", email.get("reply"))

    if request.method == "POST":
        reply = request.form["reply"]
        if reply and reply.strip():
            update_email_status(id, reply=reply)  # Save to DB

            # ✅ Send reply via SMTP
            try:
                send_email_reply(
                    user_email=session["email"],
                    app_password=session["password"],
                    to_address=email["sender"].split()[-1].strip("<>"),
                    subject=email["subject"],
                    body=reply
                )
                print(f"[📤] Sent reply to {email['sender']}")
            except Exception as e:
                print(f"[✗] SMTP send failed: {e}")

        return redirect("/inbox")

    return render_template("edit.html", email=email)

@app.route('/compose', methods=['GET', 'POST'])
def compose_email():
    ai_email = None
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            ai_email = generate_email_from_prompt(prompt)
    return render_template('compose.html', ai_email=ai_email)

@app.route('/send_composed_email', methods=['POST'])
def send_composed_email():
    from_email = session.get('email')
    app_password = session.get('password')
    to_email = request.form.get('to_email')
    subject = request.form.get('subject')
    body = request.form.get('email_content')
    files = request.files.getlist('attachments')  # 🔁 multiple files

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Bcc'] = from_email  # ✅ self-copy

    msg.attach(MIMEText(body, 'plain'))

    # Limit: 5MB per file
    max_file_size = 5 * 1024 * 1024  # 5MB

    for file in files:
        if file and file.filename:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > max_file_size:
                flash(f"⚠️ File '{file.filename}' exceeds 5MB and was skipped.")
                continue

            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=\"{file.filename}\""
            )
            msg.attach(part)

    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(from_email, app_password)
        smtp.sendmail(from_email, [to_email, from_email], msg.as_string())
        smtp.quit()
        flash("✅ Email sent with attachments (if any). A copy has been BCC’d to your inbox.")
    except Exception as e:
        flash(f"❌ Failed to send email: {str(e)}")

    return redirect(url_for('inbox'))


# ⏭ Skip
@app.route("/skip/<id>")
def skip(id):
    update_email_status(id, skip=True)
    return redirect("/inbox")

# 🚪 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

