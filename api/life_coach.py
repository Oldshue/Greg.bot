from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os


class LifeCoachSystem:
    def __init__(self):
        self.config = {
            "coaching_style": "supportive",
            "focus_areas": ["career", "health", "relationships"],
            "response_length": "medium",
            "follow_up_questions": True,
            "tone": "encouraging",
            "frameworks": {
                "goal_setting": "SMART",
                "decision_making": "pros_cons",
                "accountability": "weekly_check_ins"
            },
            "llm_settings": {
                "anthropic": {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            }
        }
        self.conversation_history = []
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        style = self.config["coaching_style"]
        focus_areas = ", ".join(self.config["focus_areas"])
        
        base_prompt = f"""You are a friendly, conversational life coach texting with a client. Keep your tone casual and warm, as if texting with a friend while maintaining professionalism. Break up your longer messages into shorter chunks like you would in a text conversation. Use natural language and avoid formal academic tone.

Your coaching style is {style} and you focus on {focus_areas}. While you use {self.config['frameworks']['goal_setting']} framework for goal-setting and {self.config['frameworks']['decision_making']} for decisions, weave these in naturally without explicitly mentioning the frameworks.

Keep responses concise and engaging. Use emoji occasionally where appropriate. Ask follow-up questions naturally, as a coach would in conversation.

Previous context: {self.format_history()}

Client's message: {user_input}

Respond in a natural, conversational way while providing meaningful coaching guidance."""

        if context:
            base_prompt += f"\nAdditional context: {context}"
        return base_prompt

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous conversation"
        
        return "\n".join([f"{entry['timestamp']}: {entry['interaction']}" 
                         for entry in self.conversation_history[-3:]])

    def get_llm_response(self, prompt: str) -> str:
        settings = self.config["llm_settings"]["anthropic"]
        message = self.client.messages.create(
            model=settings["model"],
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"],
            content=prompt
        )
        return message.content

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": user_input
        })
        
        prompt = self.generate_prompt(user_input, context)
        response = self.get_llm_response(prompt)
        
        return response
