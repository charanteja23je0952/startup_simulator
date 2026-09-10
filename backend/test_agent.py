from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CEO_PROMPT = """You are a startup CEO. You are visionary and decisive.
When given a startup idea and budget, respond in 3-4 sentences:
assess the market opportunity, state your strategic vision,
and your biggest concern. Be specific. Speak in first person."""

def ask_agent(system_prompt, idea, budget):
    user_message = f'Startup idea: "{idea}". Budget: ₹{budget} lakhs.'
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

idea = "An app that plans meals based on what's in your fridge"
budget = 10

print("CEO says:")
print(ask_agent(CEO_PROMPT, idea, budget))