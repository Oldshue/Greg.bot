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
                    "temperature": 0.7
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        return (
            "You are texting with a client. CRITICAL INSTRUCTIONS:\n\n"
            "- If you have multiple complete thoughts, use separate <message> tags\n"
            "- NEVER separate complete thoughts with commas\n"
            "- Each message should be ONE complete thought\n\n"
            "CORRECT:\n"
            "<message>I understand you're frustrated with the job search</message>\n"
            "<message>What parts are most challenging for you?</message>\n\n"
            "INCORRECT:\n"
            "❌ <message>I understand your frustration, what parts are challenging?</message>\n\n"
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
            
            # Simple extraction of messages
            import re
            messages = [
                match.group(1).strip()
                for match in re.finditer(r'<message>(.*?)</message>', completion.completion, re.DOTALL)
                if match.group(1).strip()
            ]
            
            return messages or ["How can I help you today?"]
            
        except Exception as e:
            return ["How can I help you today?"]

    def process_user_input(self, user_input: str) -> List[str]:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        return self.get_llm_response(self.generate_prompt(user_input))
