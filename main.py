from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

class AutoMailApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Email Input
        self.email_input = TextInput(hint_text='Email Address', multiline=False)
        self.layout.add_widget(self.email_input)

        # IMAP Server Input
        self.imap_input = TextInput(hint_text='IMAP Server (e.g., imap.gmail.com)', multiline=False)
        self.layout.add_widget(self.imap_input)

        # App Password Input
        self.password_input = TextInput(hint_text='App Password', multiline=False, password=True)
        self.layout.add_widget(self.password_input)

        # Submit Button
        self.submit_btn = Button(text='Login to Inbox')
        self.submit_btn.bind(on_press=self.send_login_request)
        self.layout.add_widget(self.submit_btn)

        # Result Label
        self.result_label = Label(text='Status: Waiting...')
        self.layout.add_widget(self.result_label)

        return self.layout

    def send_login_request(self, instance):
        email = self.email_input.text
        imap = self.imap_input.text
        password = self.password_input.text

        payload = {
            "email": email,
            "imap_server": imap,
            "password": password
        }

        try:
            response = requests.post("https://automail-reply.onrender.com/login", json=payload)
            if response.status_code == 200:
                self.result_label.text = "✅ Login successful. Emails fetched."
            else:
                self.result_label.text = f"❌ Error: {response.status_code} - {response.text}"
        except Exception as e:
            self.result_label.text = f"⚠️ Exception: {str(e)}"

if __name__ == '__main__':
    AutoMailApp().run()

