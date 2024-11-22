from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "focus_areas": ["career", "health", "relationships"],
            "llm_settings": {
                "anthropic": {
                    "model": "claude-2.1",
                    "max_tokens": 150,
                    "temperature": 0.7,
                    "max_message_length": 150  # Characters per message
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        history = self.format_history()
        return (
            "You are a supportive life coach texting with a client. Keep each message under 150 characters - "
            "like a text message. If you need to say more, split it into 2-3 separate short messages. "
            "Be conversational and friendly. " 
            f"Previous messages: {history}\n"
            f"Client message: {user_input}"
        )

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous messages"
        return "\n".join([msg["interaction"] for msg in self.conversation_history[-2:]])

    def split_into_messages(self, response: str) -> List[str]:
        max_length = self.config["llm_settings"]["anthropic"]["max_message_length"]
        messages = []
        
        # Split on sentence boundaries
        current_msg = ""
        sentences = response.split('. ')
        
        for sentence in sentences:
            if not sentence:
                continue
                
            if len(current_msg) + len(sentence) <= max_length:
                current_msg += sentence + '. '
            else:
                if current_msg:
                    messages.append(current_msg.strip())
                current_msg = sentence + '. '
                
        if current_msg:
            messages.append(current_msg.strip())
            
        return messages

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
            return self.split_into_messages(completion.completion)
        except Exception as e:
            return [f"Error generating response: {str(e)}"]

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
