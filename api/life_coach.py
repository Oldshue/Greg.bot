from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "llm_settings": {
                "anthropic": {
                    "model": "claude-2.1",
                    "max_tokens": 150,
                    "temperature": 0.7,
                    "max_message_length": 60
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        return (
            "You are texting with a client. Write naturally with normal sentence structure:\n\n"
            "- Use periods to separate complete thoughts\n"
            "- Use emojis on occasion when appropriate\n"
            "- Use commas normally within sentences\n"
            "- Never use commas to replace periods\n"
            "- Keep messages concise\n\n"
            f"Client message: {user_input}"
        )

    def get_llm_response(self, prompt: str) -> List[str]:
        try:
            completion = self.client.completions.create(
                model=self.config["llm_settings"]["anthropic"]["model"],
                max_tokens_to_sample=self.config["llm_settings"]["anthropic"]["max_tokens"],
                temperature=self.config["llm_settings"]["anthropic"]["temperature"],
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                stop_sequences=["\nHuman:", "\n\nHuman:"]
            )
            
            messages = []
            import re
            
            matches = re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
            for match in matches:
                message = match.group(1).strip()
                if message:
                    messages.append(message)
            
            return messages or ["How can I help you today?"]
            
        except Exception as e:
            return ["How can I help you today?"]

    def process_user_input(self, user_input: str) -> List[str]:
        return self.get_llm_response(self.generate_prompt(user_input))
