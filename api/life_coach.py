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
            "You are texting with a client. Write naturally as if texting.\n\n"
            "IMPORTANT RULES:\n"
            "1. Each complete thought should be its own message\n"
            "2. Never start a message with a conjunction (and, but, so)\n"
            "3. Never put a comma right after a period\n"
            "4. Use commas naturally within a single thought\n\n"
            "CORRECT examples:\n"
            "<message>I understand the job search is tough right now</message>\n"
            "<message>What parts feel most overwhelming?</message>\n\n"
            "INCORRECT examples:\n"
            "❌ <message>The job search is tough. And let's work on it</message>\n"
            "❌ <message>That's difficult., Let's talk about it</message>\n\n"
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
            
            # Extract messages and clean up any period-comma issues
            matches = re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
            for match in matches:
                message = match.group(1).strip()
                # Fix period-comma issues
                message = re.sub(r'\.,\s*', '. ', message)
                # Remove conjunctions at start of messages
                message = re.sub(r'^(and|but|so)\s+', '', message, flags=re.IGNORECASE)
                if message:
                    messages.append(message)
            
            return messages or ["How can I help you today?"]
            
        except Exception as e:
            return ["How can I help you today?"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input)
        return self.get_llm_response(prompt)
