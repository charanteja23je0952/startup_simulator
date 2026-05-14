from groq import Groq
import os, concurrent.futures
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

AGENTS = {
    "ceo": """You are a startup CEO. Visionary and decisive.
Respond in 3-4 sentences: assess market opportunity,
state your vision, and your biggest concern. First person.""",

    "developer": """You are a senior software developer.
Respond in 3-4 sentences: assess technical feasibility,
suggest the core tech stack, estimate MVP build time. First person.""",

    "marketer": """You are a startup growth marketer.
Respond in 3-4 sentences: identify target audience,
suggest top 2 marketing channels, estimate cost per install. First person.""",

    "investor": """You are a startup investor (VC/angel). Analytical and fair.
Respond in 3-4 sentences: evaluate market size, identify
biggest risk, give a viability score out of 10. First person."""
}

def ask_agent(role, idea, budget):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": AGENTS[role]},
            {"role": "user", "content": f'Startup idea: "{idea}". Budget: ₹{budget}.'}
        ]
    )
    return role, response.choices[0].message.content

def run_all_agents(idea, budget):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(ask_agent, role, idea, budget)
                   for role in AGENTS]
        for f in concurrent.futures.as_completed(futures):
            role, response = f.result()
            results[role] = response
    return results

if __name__ == "__main__":
    out = run_all_agents("meal planning app for fridge contents", 10)
    for role, response in out.items():
        print(f"\n{role.upper()}:\n{response}")