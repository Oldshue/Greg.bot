from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "llm_settings": {
                "anthropic": {
                    "model": "claude-2.1",
                    "max_tokens": 150,
                    "temperature": 0.7,
                    "max_message_length": 80  # Even shorter messages
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        return (
            "You are texting with a client. VERY IMPORTANT: Break your response into multiple separate, short messages "
            "of 1-2 sentences each. Each message must be under 80 characters. Use <message> tags to separate messages.\n\n"
            "Example format:\n"
            "<message>Hi! Let's talk about your resume. 📄</message>\n"
            "<message>First, use Arial or Times New Roman, 10-12pt.</message>\n"
            "<message>Keep margins at 1 inch all around.</message>\n\n"
            f"Client message: {user_input}"
        )

    def get_llm_response(self, prompt: str) -> List[str]:
        settings = self.config["llm_settings"]["anthropic"]
        try:
            completion = self.client.completions.create(
                model=settings["model"],
                max_tokens_to_sample=settings["max_tokens"],
                temperature=settings["temperature"],
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                stop_sequences=["\nHuman:", "\n\nHuman:"]
            )
            
            # Extract messages between tags
            messages = []
            response = completion.completion
            import re
            message_matches = re.finditer(r'<message>(.*?)</message>', response, re.DOTALL)
            
            for match in message_matches:
                message = match.group(1).strip()
                if len(message) <= settings["max_message_length"]:
                    messages.append(message)
            
            # If no valid tagged messages, split manually
            if not messages:
                return self.fallback_split(response, settings["max_message_length"])
                
            return messages
        except Exception as e:
            return [f"Error: {str(e)}"]

    def fallback_split(self, text: str, max_length: int) -> List[str]:
        messages = []
        current = ""
        
        for sentence in text.split('. '):
            if not sentence.strip():
                continue
                
            if len(current) + len(sentence) <= max_length:
                current += sentence + '. '
            else:
                if current:
                    messages.append(current.strip())
                current = sentence + '. '
        
        if current:
            messages.append(current.strip())
            
        return messages or ["Sorry, I had trouble breaking up my response."]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
