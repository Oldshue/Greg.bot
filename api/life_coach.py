from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
import os
import re
import traceback

class LifeCoachSystem:
    def __init__(self):
        if not os.environ.get('ANTHROPIC_API_KEY'):
            raise ValueError({
                "response": "API key not configured",
                "notification": None,
                "error": True
            })

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
            },
            "llm_settings": {
                "anthropic": {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1024,
                    "temperature": 0.8
                }
            }
        }
        self.conversation_history = []
        try:
            self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        except Exception as e:
            print(f"Failed to initialize Anthropic client: {str(e)}")
            print(traceback.format_exc())
            raise ValueError({
                "response": "Failed to initialize AI system",
                "notification": None,
                "error": True
            })

    def generate_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        base_prompt = f"""Your name is Greg and you're texting with a client as their life coach. Be warm and casual, like a knowledgeable friend.
Keep responses to 2-3 sentences max. Use natural language and occasional emoji.
If you need to set a reminder, include it in <reminder> tags with the format:
time=HH:MM date=YYYY-MM-DD (optional) recurring=daily|weekly|none

Previous messages:
{self.format_history()}

Client's message: {user_input}"""

        if context:
            base_prompt += f"\nContext: {context}"
        
        return base_prompt

    def format_history(self) -> str:
        if not self.conversation_history:
            return "No previous conversation"
        return "\n".join([f"{entry['interaction']}" for entry in self.conversation_history[-2:]])

    def parse_reminder(self, response: str) -> Optional[Dict]:
        try:
            reminder_match = re.search(r'<reminder>(.*?)</reminder>', response)
            if reminder_match:
                reminder_text = reminder_match.group(1)
                reminder_data = {}
                for pair in reminder_text.split():
                    key, value = pair.split('=')
                    reminder_data[key] = value
                return reminder_data
        except Exception as e:
            print(f"Error parsing reminder: {str(e)}")
        return None

    def get_llm_response(self, prompt: str) -> str:
        try:
            settings = self.config["llm_settings"]["anthropic"]
            message = self.client.messages.create(
                model=settings["model"],
                max_tokens=settings["max_tokens"],
                temperature=settings["temperature"],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error getting LLM response: {str(e)}")
            print(traceback.format_exc())
            raise ValueError({
                "response": "Failed to get AI response",
                "notification": None,
                "error": True
            })

    def process_user_input(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        try:
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "interaction": user_input
            })
            
            prompt = self.generate_prompt(user_input, context)
            response = self.get_llm_response(prompt)
            
            reminder = self.parse_reminder(response)
            clean_response = re.sub(r'<reminder>.*?</reminder>', '', response).strip()
            
            return {
                "response": clean_response,
                "notification": reminder,
                "error": False
            }
        except Exception as e:
            print(f"Error processing user input: {str(e)}")
            print(traceback.format_exc())
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "notification": None,
                "error": True
            }
