import os
from datetime import datetime
import anthropic

class LifeCoachSystem:
    def __init__(self):
        self.conversation_history = []
        self.client = anthropic.Client(api_key=os.environ.get('ANTHROPIC_API_KEY'))

        # Set initial greeting
        if not self.conversation_history:
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "interaction": "Hey! 👋 I'm Greg, your AI Life Coach and Accountability Partner. What can I help you with today?"
            })

    def generate_prompt(self, user_input: str) -> str:
        base_prompt = """You are Greg, a friendly and attentive AI life coach having a continuous conversation with your client. Keep your responses natural, familiar, a bit humorous, warm, and concise (2-3 sentences). You never narrate actions or describe switching personas - you simply are Greg engaging in an ongoing chat with your client.

Current conversation:
"""
        conversation = self.format_history()
        base_prompt += f"{conversation}\n\nClient: {user_input}\nGreg:"
        return base_prompt

    def format_history(self) -> str:
        if len(self.conversation_history) <= 1:  # Just the initial greeting
            return self.conversation_history[0]["interaction"]
        
        # Format recent messages as a natural conversation
        recent_messages = self.conversation_history[-3:]  # Keep last 3 messages for context
        formatted_history = []
        for msg in recent_messages:
            if msg["interaction"].startswith("Hey! 👋"):  # Initial greeting
                formatted_history.append(f"Greg: {msg['interaction']}")
            else:
                formatted_history.append(f"Client: {msg['interaction']}" if len(formatted_history) % 2 == 0 else f"Greg: {msg['interaction']}")
        return "\n".join(formatted_history)

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
        response_text = response.content[0].text
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": response_text
        })
        return response_text
