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
                    "max_message_length": 60  # Keep the message length limit
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        return (
            "You are texting with a client. Follow these rules exactly:\n\n"
            "1. Use separate <message> tags for separate thoughts\n"
            "2. Use PERIODS to end sentences, not commas\n"
            "3. Keep each message under 60 characters\n"
            "4. Write naturally as if texting\n\n"
            "CORRECT:\n"
            "<message>I understand you're frustrated with the job search.</message>\n"
            "<message>What parts are most challenging for you?</message>\n\n"
            "INCORRECT:\n"
            "❌ <message>I understand you're frustrated with the job search, what parts are challenging</message>\n"
            "❌ <message>This is hard but let's work on it, we can make progress</message>\n\n"
            f"Previous messages: {self.format_history()}\n"
            f"Client message: {user_input}"
        )

    def format_history(self) -> str:
        if not self.conversation_history:
            return "None"
        return self.conversation_history[-1]["interaction"]

    def clean_message(self, message: str) -> str:
        """Clean a single message."""
        # Convert comma-separated thoughts into separate sentences
        message = message.replace(", ", ". ").replace(",", ".")
        # Remove any connecting words that start a sentence after a period
        connecting_words = ['and ', 'but ', 'so ', 'then ']
        for word in connecting_words:
            message = message.replace(f'. {word}', '. ')
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
            
            # Extract messages and clean them
            matches = re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
            for match in matches:
                message = self.clean_message(match.group(1))
                # Split into separate messages if multiple sentences
                sentences = [s.strip() for s in message.split('.') if s.strip()]
                for sentence in sentences:
                    if sentence and len(sentence) <= self.config["llm_settings"]["anthropic"]["max_message_length"]:
                        # Add period back if it's not a question
                        if not sentence.endswith('?'):
                            sentence += '.'
                        messages.append(sentence)
            
            # If we still don't have any valid messages after all processing
            if not messages:
                return ["How can I help you today?"]
            
            return messages
            
        except Exception as e:
            return ["How can I help you today?"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input)
        return self.get_llm_response(prompt)
