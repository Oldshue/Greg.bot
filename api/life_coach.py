from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os

class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "focus_areas": ["career", "health", "relationships"],
            "response_length": "short",  # Changed from medium to short
            "follow_up_questions": True,
            "tone": "casual",  # Changed from encouraging to casual
            "frameworks": {
                "goal_setting": "SMART",
                "decision_making": "pros_cons",
                "accountability": "weekly_check_ins"
            },
            "llm_settings": {
                "anthropic": {
                    "model": "claude-2.1",
                    "max_tokens": 400,  # Reduced from 1000 to encourage conciseness
                    "temperature": 0.8  # Slightly increased to encourage more natural responses
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        # Simplified prompt that emphasizes brevity and natural conversation
        base_prompt = f"""You're texting with a client as their life coach. Be warm and casual, like a knowledgeable friend.
Keep responses under 3 short paragraphs. Use natural language and occasional emoji.
If you ask a follow-up question, limit it to one clear question.

Previous messages:
{self.format_history()}

Client's message: {user_input}"""

        if context:
            base_prompt += f"\nContext: {context}"
        
        return base_prompt

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous conversation"
        # Only show last 2 messages for more focused context
        return "\n".join([f"{entry['interaction']}" for entry in self.conversation_history[-2:]])

    def get_llm_response(self, prompt: str) -> str:
        settings = self.config["llm_settings"]["anthropic"]
        completion = self.client.completions.create(
            model=settings["model"],
            max_tokens_to_sample=settings["max_tokens"],
            temperature=settings["temperature"],
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
            stop_sequences=["\nHuman:", "\n\nHuman:"]
        )
        return completion.completion

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        prompt = self.generate_prompt(user_input, context)
        response = self.get_llm_response(prompt)
        return response
