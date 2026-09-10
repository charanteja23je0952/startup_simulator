# AI Startup Simulator

Imagine you have a business idea say, "an app that plans your meals based on what's in your fridge." Normally, validating that idea means getting time with four different experts: a CEO to judge the vision and timing, a developer to judge feasibility, a marketer to judge reach and cost, and an investor to judge risk and return. Getting all four in a room is slow and expensive.

This project simulates that room. You submit an idea and a budget; four LLM agents each playing one of those roles independently evaluate it, then debate each other across multiple rounds, referencing and pushing back on what the others said. A fifth "analyst" agent reads the full debate and distills it into a viability score, market size estimate, build-time estimate, risk level, and a recommended budget split.

Think of it as a Shark Tank you can run on any idea, instantly, in the browser.

## Features

- **Multi-agent debate, not single-shot evaluation** - CEO, Developer, Marketer, and Investor agents each hold a distinct persona and a defined stance toward the others (e.g. the Investor challenges the Marketer's cost-per-install assumptions; the Developer pushes back on the CEO's timelines).
- **3-round argument structure** - Round 1 is independent, uninfluenced opinions. Rounds 2 and 3 feed each agent the others' prior responses, so positions evolve and agents explicitly react to specific claims rather than repeating themselves.      
- **Structured analyst output** - after the debate, a separate agent call converts the unstructured discussion into a strict JSON object (viability score, market size, build time, risk level, budget split), which the frontend renders as metric cards and a Chart.js budget breakdown.
- **Parallelized inference** - each round's four agent calls run concurrently via `concurrent.futures.ThreadPoolExecutor` rather than sequentially, keeping total latency close to that of a single call per round instead of four.
- **Graceful analyst fallback** - if the analyst's JSON parsing fails (e.g. malformed model output), the app falls back to sane defaults rather than crashing the request.

## How It Works

```
User submits idea + budget
        │
        ▼
Round 1 - 4 agents answer independently (parallel)
        │
        ▼
Round 2 - each agent sees the other 3's Round 1 answers, reacts (parallel)
        │
        ▼
Round 3 - each agent sees the other 3's Round 2 answers, reacts (parallel)
        │
        ▼
Analyst agent reads all 12 responses → returns structured JSON
        │
        ▼
Frontend renders debate transcript + metric cards + budget chart
```

Each agent is a single Groq API chat completion with a role-specific system prompt that defines its personality, what it should evaluate, and who it characteristically agrees or clashes with. Round 2 and 3 prompts are dynamically built to include the other agents' previous responses, so the model is arguing with actual prior content rather than improvising a debate from scratch.

## Tech Stack

| Layer      | Technology                                  |
|------------|----------------------------------------------|
| Backend    | Python, Flask, Flask-CORS                    |
| LLM        | Groq API (`openai/gpt-oss-120b`)              |
| Concurrency| `concurrent.futures.ThreadPoolExecutor`       |
| Frontend   | HTML, CSS, vanilla JavaScript                 |
| Charts     | Chart.js                                      |
| Deployment | Backend on Render, frontend on Vercel         |

## Project Structure

```
startup_simulator/
├── backend/
│   ├── app.py            # Flask app, single /api/simulate endpoint
│   ├── agents.py         # Agent personas, debate orchestration, analyst parsing
│   ├── test_agent.py     # Standalone script to sanity-check a single agent call
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── script.js
    └── style.css
```

## Setup

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
```

Run it:

```bash
python app.py
```

The API will be live at `http://localhost:5000`, exposing a single endpoint:

```
POST /api/simulate
Body: { "idea": "string", "budget": number }
```

**Frontend**

The frontend is static open `frontend/index.html` directly, or serve the folder with any static file server. Update the API base URL in `script.js` if your backend isn't running on `localhost:5000`.

## Notes

- Groq periodically deprecates models; if you see a `model_decommissioned` error, check [Groq's deprecations page](https://console.groq.com/docs/deprecations) and update the model string in `agents.py` and `test_agent.py`.
- The analyst step expects the model to return raw JSON. If you swap models and start seeing analyst fallback values, check whether the new model wraps its output in markdown code fences - the current parsing strips a leading/trailing ` ``` ` block but may need adjusting for a different model's formatting habits.
