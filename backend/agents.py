from groq import Groq
import os, concurrent.futures, json
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

def run_analyst_agent(idea, budget, ceo, developer, marketer, investor):
    prompt = f"""You are a startup analyst. Based on the following expert opinions, return ONLY a JSON object. No explanation, no markdown, no code blocks. Just raw JSON.

Startup idea: {idea}
Budget: ₹{budget}

CEO: {ceo}
Developer: {developer}
Marketer: {marketer}
Investor: {investor}

Return exactly this structure:
{{
    "viability_score": <number 1-10>,
    "market_size": "<string like '₹4,200 Cr'>",
    "build_time": "<string like '4-6 months'>",
    "risk_level": "<Low, Medium, or High>",
    "budget_split": {{
        "development": <percentage as integer>,
        "marketing": <percentage as integer>,
        "operations": <percentage as integer>,
        "reserve": <percentage as integer>
    }}
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)

def run_all_agents(idea, budget):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(ask_agent, role, idea, budget) for role in AGENTS]
        for f in concurrent.futures.as_completed(futures):
            role, response = f.result()
            results[role] = response

    try:
        results["analyst"] = run_analyst_agent(
            idea,
            budget,
            ceo=results["ceo"],
            developer=results["developer"],
            marketer=results["marketer"],
            investor=results["investor"],
        )
    except Exception as e:
        print(f"Analyst failed: {e}")
        results["analyst"] = {
            "viability_score": 5,
            "market_size": "N/A",
            "build_time": "N/A",
            "risk_level": "Medium",
            "budget_split": {
                "development": 35,
                "marketing": 25,
                "operations": 20,
                "reserve": 20
            }
        }

    return results

if __name__ == "__main__":
    out = run_all_agents("meal planning app for fridge contents", 500000)
    for role, response in out.items():
        print(f"\n{role.upper()}:\n{response}")