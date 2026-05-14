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

function drawChart(budget) {
    const ctx = document.getElementById("budget-chart");

    const allocations = {
        "CEO / Operations": Math.round(budget * 0.20),
        "Development":      Math.round(budget * 0.35),
        "Marketing":        Math.round(budget * 0.25),
        "Investor Reserve": Math.round(budget * 0.20),
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
        const response = await fetch("http://localhost:5000/api/simulate", {
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

        responses.ceo.innerText       = data.agents.ceo       || "No response received.";
        responses.developer.innerText = data.agents.developer || "No response received.";
        responses.marketer.innerText  = data.agents.marketer  || "No response received.";
        responses.investor.innerText  = data.agents.investor  || "No response received.";

        resultsSection.style.display = "block";
        setTimeout(function() {
            resultsSection.style.opacity = "1";
        }, 10);
        drawChart(budget);
        resultsSection.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Simulation failed:", error);
        alert("Something went wrong: " + error.message + "\n\nMake sure your Flask server is running.");
    }

    setLoading(false);
}

// ── Event Listeners ──────────────────────────────────────────────
simulateBtn.addEventListener("click", simulate);