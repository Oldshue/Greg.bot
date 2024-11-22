from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "focus_areas": ["career", "health", "relationships"],
            "tone": "encouraging",
            "frameworks": {
                "goal_setting": "SMART",
                "decision_making": "pros_cons"
            },
            "llm_settings": {
                "anthropic": {
                    "model": "claude-2.1",  # Back to stable model
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        history = self.format_history()
        base_prompt = (
            "You are a supportive life coach having a text conversation. "
            "Keep responses under 100 words, friendly but professional. "
            f"Previous messages: {history}\n"
            f"Client message: {user_input}"
        )
        
        if context:
            base_prompt += f"\nContext: {context}"
        
        return base_prompt

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous messages"
        
        return "\n".join([
            f"{entry['interaction']}"
            for entry in self.conversation_history[-2:]
        ])

    def get_llm_response(self, prompt: str) -> str:
        settings = self.config["llm_settings"]["anthropic"]
        try:
            completion = self.client.completions.create(
                model=settings["model"],
                max_tokens_to_sample=settings["max_tokens"],
                temperature=settings["temperature"],
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                stop_sequences=["\nHuman:", "\n\nHuman:"]
            )
            return completion.completion
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
