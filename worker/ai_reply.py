import requests
import traceback
import os

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY")  # load from env variable
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def generate_reply(text):
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": "Reply to the email in a helpful, professional tone."},
            {"role": "user", "content": text}
        ]
    }

    try:
        print("[🧠] Sending request to OpenRouter with prompt:", text)
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()

        # 🔁 Debug AI response
        print("[🔁 AI Response]:", result)

        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("AI error:", e)
        traceback.print_exc()
        return "⚠️ AI is unavailable. Please try again later."
def generate_email_from_prompt(prompt):
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": "Write a professional, polite email based on the user's intent."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        print("[✍️] Generating composed email from prompt:", prompt)
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()

        # 🔁 Debug AI response
        print("[🔁 Compose AI Response]:", result)

        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Compose AI error:", e)
        traceback.print_exc()
        return "⚠️ Could not generate email. Please try again later."

