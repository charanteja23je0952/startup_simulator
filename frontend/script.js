// ── Element References ──────────────────────────────────────────
const ideaInput       = document.getElementById("idea-input");
const budgetSlider    = document.getElementById("budget-slider");
const budgetDisplay   = document.getElementById("budget-display");
const simulateBtn     = document.getElementById("simulate-btn");
const resultsSection  = document.getElementById("results-section");

const responses = {
    ceo:       document.getElementById("response-ceo"),
    developer: document.getElementById("response-developer"),
    marketer:  document.getElementById("response-marketer"),
    investor:  document.getElementById("response-investor"),
};

// ── Budget Slider ────────────────────────────────────────────────
budgetSlider.addEventListener("input", function() {
    const value = parseInt(budgetSlider.value);
    budgetDisplay.innerText = value.toLocaleString("en-IN");
});

// ── Loading State ────────────────────────────────────────────────
function setLoading(isLoading) {
    if (isLoading) {
        simulateBtn.disabled = true;
        simulateBtn.innerText = "⏳ Simulating...";
        Object.values(responses).forEach(function(el) {
            el.innerText = "Thinking...";
        });
    } else {
        simulateBtn.disabled = false;
        simulateBtn.innerText = "⚡ Simulate My Startup";
    }
}

// ── Validation ───────────────────────────────────────────────────
function validate() {
    const idea = ideaInput.value.trim();
    if (idea === "") {
        alert("Please enter a startup idea first.");
        ideaInput.focus();
        return false;
    }
    if (idea.length < 10) {
        alert("Please describe your idea in a bit more detail.");
        ideaInput.focus();
        return false;
    }
    return true;
}

// ── Chart ────────────────────────────────────────────────────────
let chartInstance = null;

function drawChart(budget, budgetSplit) {
    const ctx = document.getElementById("budget-chart");

    const allocations = {
        "Development":  Math.round(budget * budgetSplit.development / 100),
        "Marketing":    Math.round(budget * budgetSplit.marketing / 100),
        "Operations":   Math.round(budget * budgetSplit.operations / 100),
        "Reserve":      Math.round(budget * budgetSplit.reserve / 100),
    };

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(allocations),
            datasets: [{
                label: "Budget Allocation (₹)",
                data: Object.values(allocations),
                backgroundColor: ["#6c63ff", "#00d4aa", "#ff6b6b", "#ffd93d"],
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return "₹" + context.raw.toLocaleString("en-IN");
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: "#8b8fa8",
                        callback: function(value) {
                            return "₹" + value.toLocaleString("en-IN");
                        }
                    },
                    grid: { color: "#2a2d3e" }
                },
                x: {
                    ticks: { color: "#8b8fa8" },
                    grid: { display: false }
                }
            }
        }
    });
}

// ── Main Simulate Function ───────────────────────────────────────
async function simulate() {

    if (!validate()) return;

    const idea   = ideaInput.value.trim();
    const budget = parseInt(budgetSlider.value);

    setLoading(true);
    document.getElementById("idea-summary-text").innerText = idea;

    try {
        const response = await fetch("https://startup-simulator-backend.onrender.com/api/simulate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                idea:   idea,
                budget: budget
            })
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const data = await response.json();
        console.log("API response:", data);

        responses.ceo.innerText       = data.round1.ceo       || "No response received.";
        responses.developer.innerText = data.round1.developer || "No response received.";
        responses.marketer.innerText  = data.round1.marketer  || "No response received.";
        responses.investor.innerText  = data.round1.investor  || "No response received.";
 
        const analyst = data.analyst;
        document.getElementById("metric-viability-value").innerText = analyst.viability_score;
        document.getElementById("metric-market-value").innerText    = analyst.market_size;
        document.getElementById("metric-build-value").innerText     = analyst.build_time;
         
        const rounds = ["r2", "r3"];
        const roundData = { r2: data.round2, r3: data.round3 };
        const agents = ["ceo", "developer", "marketer", "investor"];

        rounds.forEach(function(round) {
            agents.forEach(function(agent) {
                const bubble = document.getElementById(`debate-${round}-${agent}`);
                if (bubble) {
                    bubble.querySelector(".bubble-text").innerText =
                        roundData[round][agent] || "No response.";
                }
            });
        });
         
        const riskEl = document.getElementById("metric-risk-value");
        riskEl.innerText = analyst.risk_level;
        riskEl.className = analyst.risk_level.toLowerCase();
        resultsSection.style.display = "block";
        setTimeout(function() {
            resultsSection.style.opacity = "1";
        }, 10);
        drawChart(budget, analyst.budget_split);
        resultsSection.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Simulation failed:", error);
        alert("Something went wrong: " + error.message + "\n\nMake sure your Flask server is running.");
    }

    setLoading(false);
}

// ── Event Listeners ──────────────────────────────────────────────
simulateBtn.addEventListener("click", simulate);