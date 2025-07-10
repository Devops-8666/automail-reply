import requests
import traceback

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer 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",  # Replace with your OpenRouter API key
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

