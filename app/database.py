from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://mongodb:27017/")
db = client["automail"]
emails_col = db["emails"]

def save_emails(emails, user_email):
    for email in emails:
        email["user"] = user_email
        email["status"] = "unread"
        if not emails_col.find_one({"subject": email["subject"], "sender": email["sender"], "user": user_email}):
            emails_col.insert_one(email)

def get_emails(user_email):
    return list(emails_col.find({ "user": user_email }))

def get_email_by_id(id):
    return emails_col.find_one({"_id": ObjectId(id)})

def update_email_status(id, reply=None, skip=False):
    update = {"$set": {"status": "skipped" if skip else "replied"}}
    if reply:
        update["$set"]["reply"] = reply
    emails_col.update_one({"_id": ObjectId(id)}, update)

def clear_emails_for_user(user_email):
    emails_col.delete_many({ "user": user_email })
def update_reply_only(id, reply):
    emails_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"reply": reply}}
    )


