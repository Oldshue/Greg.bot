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
            "You are sending text messages to a client. FOLLOW THESE RULES EXACTLY:\n\n"
            "1. Each <message> must be a SINGLE complete thought\n"
            "2. NEVER use commas within messages\n"
            "3. NEVER connect multiple thoughts\n"
            "4. Keep each message under 60 characters\n"
            "5. Write naturally like you're texting\n"
            "6. Send 1-3 messages as feels natural\n\n"
            "CORRECT FORMAT:\n"
            "<message>I hear you're having trouble with job search</message>\n"
            "<message>What part is most challenging?</message>\n\n"
            "INCORRECT FORMAT:\n"
            "❌ <message>I hear you're having trouble, let's break it down</message>\n"
            "❌ <message>First we'll look at your resume, then interview prep</message>\n\n"
            f"Previous messages: {self.format_history()}\n"
            f"Client message: {user_input}\n\n"
            "Respond naturally with 1-3 messages:"
        )

    def format_history(self) -> str:
        if not self.conversation_history:
            return "None"
        return self.conversation_history[-1]["interaction"]

    def clean_message(self, message: str) -> str:
        """Strictly clean a single message."""
        # If message contains a comma, only keep the first part
        message = message.split(',')[0]
        # Remove any connecting words that might indicate multiple thoughts
        connecting_words = [' and ', ' but ', ' or ', ' then ', ' so ']
        for word in connecting_words:
            if word in message.lower():
                message = message.split(word)[0]
        return message.strip()

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
            
            # Extract and strictly clean each message
            matches = re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
            for match in matches:
                message = self.clean_message(match.group(1))
                if message and len(message) <= 60:
                    messages.append(message)
            
            # If we don't have any valid messages, create a single fallback
            if not messages:
                return ["How can I help you today?"]
            
            return messages
            
        except Exception as e:
            return ["I'm here to help"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input)
        return self.get_llm_response(prompt)
