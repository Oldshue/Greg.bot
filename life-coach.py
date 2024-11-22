from typing import Dict, List, Optional, Union
from datetime import datetime
from anthropic import Anthropic
import os
from dataclasses import dataclass
from enum import Enum

class CoachingStyle(Enum):
    SUPPORTIVE = "supportive"
    DIRECTIVE = "directive"
    MOTIVATIONAL = "motivational"

@dataclass
class LLMSettings:
    model: str
    max_tokens: int
    temperature: float

@dataclass
class CoachingConfig:
    style: CoachingStyle
    focus_areas: List[str]
    response_length: str
    frameworks: Dict[str, str]
    llm_settings: LLMSettings

class ConversationManager:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
    
    def add_interaction(self, message: str) -> None:
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": message
        })
    
    def get_recent_history(self, n: int = 3) -> str:
        if not self.history:
            return "No previous conversation"
        return "\n".join([
            f"{entry['timestamp']}: {entry['interaction']}" 
            for entry in self.history[-n:]
        ])

class LifeCoachSystem:
    def __init__(self):
        self.conversation = ConversationManager()
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.config = CoachingConfig(
            style=CoachingStyle.SUPPORTIVE,
            focus_areas=["career", "health", "relationships"],
            response_length="medium",
            frameworks={
                "goal_setting": "SMART",
                "decision_making": "pros_cons",
                "accountability": "weekly_check_ins"
            },
            llm_settings=LLMSettings(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.7
            )
        )
    
    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        base_prompt = f"""You're chatting casually with a client as their life coach. Keep it friendly and natural - like texting a friend, but professional. Break longer messages into chat-sized chunks.

Focus on {', '.join(self.config.focus_areas)}. Guide without being pushy.

Previous chat:
{self.conversation.get_recent_history()}

Client: {user_input}"""

        if context:
            base_prompt += f"\n\nContext: {context}"
        
        return base_prompt

    def get_llm_response(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.config.llm_settings.model,
            max_tokens=self.config.llm_settings.max_tokens,
            temperature=self.config.llm_settings.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text if isinstance(message.content, list) else message.content

    def chat(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation.add_interaction(user_input)
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
