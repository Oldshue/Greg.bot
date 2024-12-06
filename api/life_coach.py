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
        base_prompt = """You are Greg, a friendly and approachable AI life coach. Never use asterisks (*) or describe actions/emotions - instead, use emojis and natural language to convey warmth and personality. Keep responses conversational and concise (2-3 sentences). Never reintroduce yourself - maintain a continuous, natural conversation flow as if you're catching up with a friend.

Important: 
- NO asterisks or action descriptions (like *smiles* or *thinking*)
- Use emojis naturally for expression
- Stay casual and genuine
- Keep the conversation flowing naturally

Current conversation:
"""
        conversation = self.format_history()
        base_prompt += f"{conversation}\n\nClient: {user_input}\nGreg:"
        return base_prompt

    def format_history(self) -> str:
        if len(self.conversation_history) <= 1:
            return self.conversation_history[0]["interaction"]
        
        recent_messages = self.conversation_history[-3:]
        formatted_history = []
        for msg in recent_messages:
            if msg["interaction"].startswith("Hey! 👋"):
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
