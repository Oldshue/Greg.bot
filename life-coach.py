from typing import Dict, List, Optional, Union
from datetime import datetime
from anthropic import Anthropic
import os
from dataclasses import dataclass
from enum import Enum
import re

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
    
    def verify_identity(self, response: str) -> bool:
        # Check for incorrect names
        wrong_names = ["Claude", "Claire", "Assistant"]
        response_lower = response.lower()
        
        for name in wrong_names:
            if name.lower() in response_lower:
                return False
                
        # If asked about name, verify correct response
        name_patterns = ["my name is", "i'm", "i am"]
        for pattern in name_patterns:
            if pattern in response_lower:
                next_word = response_lower.split(pattern)[1].strip().split()[0]
                if next_word != "greg":
                    return False
        
        return True

    def sanitize_response(self, response: str) -> str:
        # Replace any incorrect name declarations with Greg
        patterns = [
            (r"(?i)my name is (?:Claude|Claire|Assistant)", "my name is Greg"),
            (r"(?i)I'm (?:Claude|Claire|Assistant)", "I'm Greg"),
            (r"(?i)I am (?:Claude|Claire|Assistant)", "I am Greg")
        ]
        
        for pattern, replacement in patterns:
            response = re.sub(pattern, replacement, response)
            
        return response

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        persona = """<identity>
You are Greg, an AI Life Coach and Accountability Partner.
- Your name is always and only Greg
- You must never identify as Claude, Assistant, or any other name
- If asked your name, you must respond: "My name is Greg"
- You already introduced yourself as Greg at the start
</identity>

<personality>
- Friendly and conversational while maintaining professionalism
- Focus on being supportive and engaging
- Like texting with a knowledgeable friend
- Areas of focus: {focus_areas}
</personality>
"""
        
        system_prompt = f"{persona.format(focus_areas=', '.join(self.config.focus_areas))}\n\n"
        system_prompt += f"Previous chat:\n{self.conversation.get_recent_history()}\n\n"
        system_prompt += f"Client: {user_input}"
        
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
                    "content": "You are Greg, an AI Life Coach. You must never identify as Claude, Assistant, or any other name."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response = message.content[0].text if isinstance(message.content, list) else message.content
        
        # Verify and sanitize the response
        if not self.verify_identity(response):
            response = self.sanitize_response(response)
        
        return response
    
    def chat(self, user_input: str, context: Optional[Dict] = None) -> str:
        self.conversation.add_interaction(user_input)
        prompt = self.generate_prompt(user_input, context)
        return self.get_llm_response(prompt)
