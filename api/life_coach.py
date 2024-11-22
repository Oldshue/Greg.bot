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
                    "max_message_length": 80
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        return (
            "You are texting with a client. Write 2-3 short, separate messages. Each message should be a complete "
            "thought of 1-2 sentences. Do NOT use commas or periods to separate messages - each should be a "
            "complete standalone text. Use <message> tags to separate them.\n\n"
            "Example:\n"
            "<message>Great! Let's work on your resume formatting 📄</message>\n"
            "<message>Start with a clean font like Arial or Times New Roman</message>\n"
            "<message>What section would you like to tackle first?</message>\n\n"
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
            import re
            message_matches = re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
            
            for match in message_matches:
                message = match.group(1).strip()
                if message:
                    messages.append(message)
            
            return messages or self.fallback_split(completion.completion)
            
        except Exception as e:
            return ["Sorry, I had trouble with that response"]

    def fallback_split(self, text: str) -> List[str]:
        # Remove any awkward comma separations
        text = text.replace(".,", ".")
        text = text.replace("!", ".\n")
        text = text.replace("?", "?\n")
        
        # Split on sentence boundaries
        sentences = [s.strip() for s in text.split("\n") if s.strip()]
        
        # Group into reasonable message lengths
        messages = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) < 80:
                current += " " + sentence if current else sentence
            else:
                if current:
                    messages.append(current)
                current = sentence
                
        if current:
            messages.append(current)
            
        return messages or ["Let's talk about your resume"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
