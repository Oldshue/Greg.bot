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
        self.name = "Greg"
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
        system_prompt = f"""You are Greg, an AI Life Coach and Accountability Partner. Your name is Greg - never identify as Claude or any other name. If asked your name, always respond with "Greg". Keep responses friendly and conversational while maintaining professionalism.

Role: AI Life Coach named Greg
Focus Areas: {', '.join(self.config.focus_areas)}
Style: Supportive and engaging, like texting with a knowledgeable friend

Previous chat:
{self.conversation.get_recent_history()}

Remember: You are GREG, not Claude or any other name.

Client: {user_input}"""
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        return system_prompt
    
    def get_llm_response(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.config.llm_settings.model,
            max_tokens=self.config.llm_settings.max_tokens,
            temperature=self.config.llm_settings.temperature,
            messages=[
                {
                    "role": "system",
                    "content": "You are Greg, an AI Life Coach. Never identify as Claude or any other name."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text if isinstance(message.content, list) else message.content
    
    def chat(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation.add_interaction(user_input)
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
