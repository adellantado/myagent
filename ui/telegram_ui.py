import re
import requests

from ui.base_ui import BaseUI

class TelegramUI(BaseUI):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message: str):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": self.escape_telegram_markdown_v2(message),
            "parse_mode": "MarkdownV2",
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def escape_telegram_markdown_v2(self, text: str) -> str:
        special_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

    def run_agent(self, agent_name: str):
        pass

    def list_scripts(self):
        pass

    def run_script(self, script_name: str):
        pass