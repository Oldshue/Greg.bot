from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "focus_areas": ["career", "health", "relationships", "goals"],
            "response_length": "short",
            "follow_up_questions": True,
            "tone": "casual",
            "frameworks": {
                "goal_setting": "SMART",
                "decision_making": "pros_cons",
                "accountability": "weekly_check_ins"
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        base_prompt = f"""Your name is Greg and you're texting with a client as their life coach. Be warm and casual, like a knowledgeable friend.
Keep responses to 2-3 sentences max. Use natural language and occasional emoji.

Previous messages:
{self.format_history()}

Client's message: {user_input}"""
        return base_prompt

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous conversation"
        return "\n".join([f"{entry['interaction']}" for entry in self.conversation_history[-2:]])

    def process_user_input(self, user_input: str) -> str:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        prompt = self.generate_prompt(user_input)
        message = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
