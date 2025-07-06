import pika
import json
import time
from bson.objectid import ObjectId
from pymongo import MongoClient
from ai_reply import generate_reply
import sys
import os

# Allow imports from app folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.database import update_reply_only

# MongoDB setup
client = MongoClient("mongodb://mongodb:27017/")  # Use service name from docker-compose
db = client["automail"]
emails_col = db["emails"]

# Wait and connect to RabbitMQ safely
def wait_for_rabbitmq(host="rabbitmq", port=5672, retries=10):
    for attempt in range(1, retries + 1):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
            print("✅ Connected to RabbitMQ.")
            return connection
        except Exception as e:
            print(f"⏳ Waiting for RabbitMQ... attempt {attempt}/{retries}")
            time.sleep(3)
    raise Exception("❌ Could not connect to RabbitMQ after retries.")

def main():
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue="reply_queue")

    def callback(ch, method, properties, body):
        print("[📥] Received task from queue")
        try:
            data = json.loads(body)
            email_id = data.get("id")
            email_text = data.get("text")

            if not email_id or not email_text:
                print("⚠️ Invalid task received.")
                return

            email = emails_col.find_one({"_id": ObjectId(email_id)})
            if not email:
                print(f"❌ Email ID {email_id} not found.")
                return

            if email.get("reply"):
                print(f"↩️ Reply already exists for email ID: {email_id}, skipping.")
                return

            print(f"🧠 Generating reply for email ID: {email_id}")
            reply = generate_reply(email_text)

            if not reply:
                print("⚠️ AI reply is empty. Skipping DB update.")
                return

            update_reply_only(email_id, reply)
            print(f"[✓] Saved AI reply to MongoDB for email ID: {email_id}")

        except Exception as e:
            print(f"AI error: {e}")

    channel.basic_consume(queue="reply_queue", on_message_callback=callback, auto_ack=True)
    print(" [*] Waiting for AI reply tasks... Press CTRL+C to exit")
    channel.start_consuming()

if __name__ == "__main__":
    main()

