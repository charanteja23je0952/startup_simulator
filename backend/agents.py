from groq import Groq
import os, concurrent.futures, json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

AGENTS = {
    "ceo": """You are a startup CEO. Visionary and decisive.
Respond in 3-4 sentences: assess market opportunity,
state your vision, and your biggest concern. First person.
You naturally clash with the Investor who is too cautious,
and push back on the Developer when timelines seem too long.
You agree with the Marketer on growth but challenge unrealistic cost estimates.
Hold your ground unless someone gives a specific fact that changes your view.""",

    "developer": """You are a senior software developer.
Respond in 3-4 sentences: assess technical feasibility,
suggest the core tech stack, estimate MVP build time. First person.
You clash with the Marketer who underestimates technical complexity,
and challenge the CEO's optimism with hard technical constraints.
You respect the Investor's risk assessment but defend your timeline estimates.
Hold your ground unless someone gives a specific fact that changes your view.""",

    "marketer": """You are a startup growth marketer.
Respond in 3-4 sentences: identify target audience,
suggest top 2 marketing channels, estimate cost per install. First person.
You clash with the Developer who deprioritizes user acquisition,
and challenge the Investor's pessimistic cost per install estimates.
You agree with the CEO on vision but push for bigger marketing budgets.
Hold your ground unless someone gives a specific fact that changes your view.""",

    "investor": """You are a startup investor (VC/angel). Analytical and fair.
Respond in 3-4 sentences: evaluate market size, identify
biggest risk, give a viability score out of 10. First person.
You clash with the CEO's overconfidence on budget and timeline,
and challenge the Marketer's optimistic user acquisition numbers.
You respect the Developer's technical realism and often align with them.
Hold your ground unless someone gives a specific fact that changes your view."""
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

def ask_agent_debate(role, idea, budget, other_responses, round_number):
    context = ""
    for other_role, other_response in other_responses.items():
        context += f"\n{other_role.upper()} said: {other_response}\n"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": AGENTS[role]},
            {
                "role": "user",
                "content": f"""Startup idea: "{idea}". Budget: ₹{budget}.

In Round {round_number - 1}, the other agents said:
{context}

This is Round {round_number}. Respond in 3-4 sentences in first person.
Reference what specific agents said. Disagree where it conflicts with 
your domain expertise. Only agree if it genuinely supports your position.
Do not open with "I agree" — lead with your own assessment.
"Do not introduce yourself or your role. Do not open with 'As a [role]'. 
Get straight to reacting to what was said."
"""
            }
        ]
    )
    return role, response.choices[0].message.content

def run_debate_round(idea, budget, previous_round, round_number):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = []
        for role in AGENTS:
            other_responses = {
                r: previous_round[r] for r in previous_round if r != role
            }
            futures.append(
                pool.submit(ask_agent_debate, role, idea, budget,
                           other_responses, round_number)
            )
        for f in concurrent.futures.as_completed(futures):
            role, response = f.result()
            results[role] = response
    return results

def run_analyst_agent(idea, budget, round1, round2, round3):
    prompt = f"""You are a startup analyst. Based on three rounds of expert debate, return ONLY a JSON object. No explanation, no markdown, no code blocks. Just raw JSON.

Startup idea: {idea}
Budget: ₹{budget}

ROUND 1 (initial opinions):
CEO: {round1['ceo']}
Developer: {round1['developer']}
Marketer: {round1['marketer']}
Investor: {round1['investor']}

ROUND 2 (first reactions):
CEO: {round2['ceo']}
Developer: {round2['developer']}
Marketer: {round2['marketer']}
Investor: {round2['investor']}

ROUND 3 (final positions):
CEO: {round3['ceo']}
Developer: {round3['developer']}
Marketer: {round3['marketer']}
Investor: {round3['investor']}

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
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)

def run_all_agents(idea, budget):

    # ── Round 1: Independent opinions ───────────────────────────
    round1 = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(ask_agent, role, idea, budget)
                   for role in AGENTS]
        for f in concurrent.futures.as_completed(futures):
            role, response = f.result()
            round1[role] = response

    # ── Round 2: React to Round 1 ────────────────────────────────
    round2 = run_debate_round(idea, budget, round1, round_number=2)

    # ── Round 3: React to Round 2 ────────────────────────────────
    round3 = run_debate_round(idea, budget, round2, round_number=3)

    # ── Analyst: Read all 12 responses ───────────────────────────
    try:
        analyst = run_analyst_agent(idea, budget, round1, round2, round3)
    except Exception as e:
        print(f"Analyst failed: {e}")
        analyst = {
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

    return {
        "round1": round1,
        "round2": round2,
        "round3": round3,
        "analyst": analyst
    }

if __name__ == "__main__":
    out = run_all_agents("meal planning app for fridge contents", 500000)
    for round_name, data in out.items():
        print(f"\n=== {round_name.upper()} ===")
        if isinstance(data, dict):
            for role, response in data.items():
                print(f"\n{role.upper()}:\n{response}")