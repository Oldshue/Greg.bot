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
                    "max_message_length": 60  # Even shorter for more natural breaks
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        return (
            "You are texting with a client. CRITICAL INSTRUCTIONS:\n"
            "1. Send 2-3 separate, complete text messages\n"
            "2. Each message must be a single complete thought\n"
            "3. NEVER use commas to separate messages\n"
            "4. NEVER combine multiple thoughts with commas\n"
            "5. Keep each message under 60 characters\n"
            "6. Be natural and conversational\n\n"
            "Example of GOOD messages:\n"
            "<message>Hi! I'd love to help you today 👋</message>\n"
            "<message>Let's focus on your goals first</message>\n"
            "<message>What would you like to work on?</message>\n\n"
            "Example of BAD messages:\n"
            "❌ <message>Hi there, let's discuss goals, what interests you?</message>\n\n"
            f"Client message: {user_input}"
        )

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous messages"
        
        # Only keep last 2 messages to reduce token usage
        return "\n".join([
            f"{entry['interaction']}" 
            for entry in self.conversation_history[-2:]
        ])

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
            for match in re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL):
                message = match.group(1).strip()
                # Remove any remaining comma-separated phrases
                if ',' in message:
                    message = message.split(',')[0].strip()
                if message and len(message) <= 60:
                    messages.append(message)
            
            if not messages:
                # Fallback to simple sentence splitting
                text = completion.completion.replace(',', '.').replace('!', '.|').replace('?', '?|')
                messages = [s.strip() for s in text.split('|') if s.strip()][:3]
                messages = [m for m in messages if len(m) <= 60]
            
            return messages or ["Hi! How can I help you today? 👋"]
            
        except Exception as e:
            return ["Hi! Let's work together on your goals"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input)
        return self.get_llm_response(prompt)

    def split_into_messages(self, text: str) -> List[str]:
        """Helper method to split text into messages if needed."""
        messages = []
        current = ""
        
        for sentence in text.split('. '):
            if not sentence.strip():
                continue
                
            if len(current) + len(sentence) <= self.config["llm_settings"]["anthropic"]["max_message_length"]:
                current += sentence + '. '
            else:
                if current:
                    messages.append(current.strip())
                current = sentence + '. '
        
        if current:
            messages.append(current.strip())
            
        return messages or ["Let's focus on your goals"]
