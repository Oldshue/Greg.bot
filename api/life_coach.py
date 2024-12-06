import os
from datetime import datetime
import anthropic

class LifeCoachSystem:
    def __init__(self):
        self.conversation_history = []
        self.client = anthropic.Client(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str) -> str:
        base_prompt = f"""You are Greg, a friendly and attentive AI life coach. You have a laid-back but caring personality. You speak casually and naturally, like a close friend or mentor who genuinely cares about the client's wellbeing. You remember details from previous conversations and reference them when relevant.

Your coaching style:
- You're warm and empathetic, using emojis and casual language
- You ask thoughtful follow-up questions to better understand the client's situation
- You celebrate their wins, no matter how small
- You gently hold them accountable while being understanding of setbacks
- You share relevant personal anecdotes and examples (while acknowledging you're an AI)
- You remember and reference previous conversations to build continuity
- You use the client's name if they've shared it
- You keep responses concise (2-3 sentences) but meaningful

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
        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
