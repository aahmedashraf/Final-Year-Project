document.addEventListener("DOMContentLoaded", () => {
  initializeChart();
  loadDailyData();
  loadWeeklyData();
  checkForFinalizedDay(); // Check if today's daily score exists and display finalize panel if so

  // Attach the Finalize Daily Log button handler
  const confirmDayBtn = document.getElementById("confirmDayBtn");
  if (confirmDayBtn) {
    confirmDayBtn.addEventListener("click", confirmDay);
  }

  // Attach the View Score Breakdown button handler (if exists)
  const viewBreakdownBtn = document.getElementById("viewBreakdownBtn");
  if (viewBreakdownBtn) {
    viewBreakdownBtn.addEventListener("click", showDailyBreakdown);
  }

  // NEW: Attach the Portion Guide link handler (small text next to log your meals)
  const portionGuideLink = document.getElementById("viewPortionGuideLink");
  if (portionGuideLink) {
    portionGuideLink.addEventListener("click", (e) => {
      e.preventDefault();
      showPortionGuide();
    });
  }
});

// DOM Elements
const foodSearch = document.getElementById("foodSearch");
const foodSuggestions = document.getElementById("foodSuggestions");
const diaryTable = document.getElementById("diaryTable").querySelector("tbody");
const addFoodBtn = document.getElementById("addFoodBtn");
const logoutBtn = document.getElementById("logoutBtn");
const finalizePanel = document.getElementById("finalizePanel");
let scoreChart = null;

// Event Listeners
addFoodBtn.addEventListener("click", addFoodToDiary);
logoutBtn.addEventListener("click", logout);
foodSearch.addEventListener("input", handleFoodSearch);
foodSuggestions.addEventListener("click", handleSuggestionClick);

// Chart Initialization
function initializeChart() {
  const ctx = document.getElementById("scoreChart").getContext("2d");
  scoreChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [], // Dates will be filled in from your weekly data
      datasets: [
        {
          label: "Weekly Inflammation Trend",
          data: [],
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.2)",
          tension: 0.1,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        tooltip: {
          callbacks: {
            title: (tooltipItems) => {
              // Show the date as the title
              return tooltipItems[0].label;
            },
            label: (tooltipItem) => {
              // Show the score with extra formatting
              return "Score: " + tooltipItem.formattedValue;
            },
            footer: (tooltipItems) => {
              const score = tooltipItems[0].parsed.y;
              if (score > 0) {
                return "Pro-Inflammatory";
              } else if (score < 0) {
                return "Anti-Inflammatory";
              } else {
                return "Neutral";
              }
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: "Inflammation Score",
            font: {
              size: 14,
            },
          },
          grid: {
            color: "rgba(0, 0, 0, 0.1)",
          },
        },
        x: {
          title: {
            display: true,
            text: "Date",
            font: {
              size: 14,
            },
          },
          grid: {
            display: false,
          },
        },
      },
    },
  });
}

// Check if today's log is finalized by calling /get_daily_score
async function checkForFinalizedDay() {
  try {
    const response = await fetch("/get_daily_score");
    if (!response.ok) return;
    const data = await response.json();
    if (data.daily_dii_score !== null) {
      const scoreEl = document.getElementById("dailyDiiScoreDisplay");
      scoreEl.textContent =
        "Overall DII Score: " + data.daily_dii_score.toFixed(2);
      let feedbackHTML = "";
      if (data.daily_dii_score > 0) {
        scoreEl.classList.remove("anti-inflammatory");
        scoreEl.classList.add("pro-inflammatory");
        feedbackHTML = `
          <p>Your overall diet appears to be <strong>pro-inflammatory</strong>.</p>
          <p>To help reduce inflammation, consider incorporating more anti-inflammatory foods such as:</p>
          <p>
            Leafy greens (e.g., spinach, kale)<br>
            Fatty fish (e.g., salmon, mackerel)<br>
            Berries (e.g., blueberries, strawberries)<br>
            Nuts and seeds (e.g., almonds, walnuts)<br>
            Olive oil<br>
            Whole grains
          </p>
          <p>For more guidance, see 
             <a href="https://www.healthline.com/nutrition/anti-inflammatory-diet-101" target="_blank">
               Healthline's Anti-Inflammatory Diet Guide
             </a>
          </p>
        `;
      } else if (data.daily_dii_score < 0) {
        scoreEl.classList.remove("pro-inflammatory");
        scoreEl.classList.add("anti-inflammatory");
        feedbackHTML = `
          <p>Great job! Your overall diet appears to be <strong>anti-inflammatory</strong>.</p>
          <p>Keep up including nutrient-rich, anti-inflammatory foods such as:</p>
          <p>
            Leafy greens (e.g., spinach, kale)<br>
            Fatty fish (e.g., salmon, mackerel)<br>
            Berries and other fruits<br>
            Nuts and seeds<br>
            Olive oil<br>
            Whole grains
          </p>
          <p>For further ideas, please refer to 
             <a href="https://www.healthline.com/nutrition/anti-inflammatory-diet-101" target="_blank">
               Healthline's Anti-Inflammatory Diet Guide
             </a>.
          </p>
        `;
      } else {
        scoreEl.classList.remove("pro-inflammatory", "anti-inflammatory");
        feedbackHTML = `<p>Your overall diet is neutral. Consider small adjustments, such as adding more fruits and vegetables, to further enhance its anti-inflammatory benefits.</p>`;
      }
      document.getElementById("scoreFeedback").innerHTML = feedbackHTML;
      window["dailyBreakdown"] = data.breakdown;
      finalizePanel.style.display = "block";
    }
  } catch (error) {
    console.error("Error checking finalized day:", error);
  }
}

// Food Search Handler
async function handleFoodSearch() {
  const query = foodSearch.value.trim();
  foodSuggestions.innerHTML = "";
  if (query.length < 3) return;
  try {
    const response = await fetch(
      `/usda-proxy?query=${encodeURIComponent(query)}`
    );
    if (!response.ok) throw new Error("Failed to fetch food data");
    const data = await response.json();
    if (data.foods && data.foods.length > 0) {
      data.foods.forEach((food) => {
        const li = document.createElement("li");
        li.textContent = food.description;
        li.dataset.fdcId = food.fdcId;
        foodSuggestions.appendChild(li);
      });
    } else {
      foodSuggestions.innerHTML = "<li>No results found</li>";
    }
  } catch (error) {
    console.error("Search error:", error);
    alert("Failed to search foods");
  }
}

// Suggestion Click Handler
function handleSuggestionClick(event) {
  if (event.target.tagName === "LI") {
    foodSearch.value = event.target.textContent;
    foodSuggestions.innerHTML = "";
    addFoodBtn.disabled = false;
  }
}

// Add Food to Diary
async function addFoodToDiary() {
  const food = foodSearch.value.trim();
  const quantity = parseFloat(document.getElementById("foodQuantity").value);
  if (!food || isNaN(quantity) || quantity <= 0) {
    alert("Please enter valid food and quantity");
    return;
  }
  try {
    const response = await fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ food_name: food, quantity: quantity }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to log food");
    }
    const result = await response.json();
    foodSearch.value = "";
    document.getElementById("foodQuantity").value = "";
    addFoodBtn.disabled = true;
    loadDailyData();
    loadWeeklyData();
  } catch (error) {
    console.error("Add food error:", error);
    alert(error.message || "Failed to add food");
  }
}

// Confirm Day Handler: Finalizes today's log.
async function confirmDay() {
  try {
    const response = await fetch("/confirm_day", { method: "POST" });
    if (!response.ok) throw new Error("Failed to finalize daily log");
    const data = await response.json();
    const scoreEl = document.getElementById("dailyDiiScoreDisplay");
    scoreEl.textContent =
      "Overall DII Score: " + data.daily_dii_score.toFixed(2);
    let feedbackHTML = "";
    if (data.daily_dii_score > 0) {
      scoreEl.classList.remove("anti-inflammatory");
      scoreEl.classList.add("pro-inflammatory");
      feedbackHTML = `
          <p>Your overall diet appears to be <strong>pro-inflammatory</strong>.</p>
          <p>To help reduce inflammation, consider incorporating more anti-inflammatory foods such as:</p>
          <p>
            Leafy greens (e.g., spinach, kale)<br>
            Fatty fish (e.g., salmon, mackerel)<br>
            Berries (e.g., blueberries, strawberries)<br>
            Nuts and seeds (e.g., almonds, walnuts)<br>
            Olive oil<br>
            Whole grains
          </p>
          <p>For more guidance, see 
             <a href="https://www.healthline.com/nutrition/anti-inflammatory-diet-101" target="_blank">
               Healthline's Anti-Inflammatory Diet Guide
             </a>
          </p>
        `;
    } else if (data.daily_dii_score < 0) {
      scoreEl.classList.remove("pro-inflammatory");
      scoreEl.classList.add("anti-inflammatory");
      feedbackHTML = `
          <p>Great job! Your overall diet appears to be <strong>anti-inflammatory</strong>.</p>
          <p>Keep up including nutrient-rich, anti-inflammatory foods such as:</p>
          <p>
            Leafy greens (e.g., spinach, kale)<br>
            Fatty fish (e.g., salmon, mackerel)<br>
            Berries and other fruits<br>
            Nuts and seeds<br>
            Olive oil<br>
            Whole grains
          </p>
          <p>For further ideas, please refer to 
             <a href="https://www.healthline.com/nutrition/anti-inflammatory-diet-101" target="_blank">
               Healthline's Anti-Inflammatory Diet Guide
             </a>.
          </p>
        `;
    } else {
      scoreEl.classList.remove("pro-inflammatory", "anti-inflammatory");
      feedbackHTML = `<p>Your overall diet is neutral. Consider small adjustments, such as adding more fruits and vegetables, to further enhance its anti-inflammatory benefits.</p>`;
    }
    document.getElementById("scoreFeedback").innerHTML = feedbackHTML;
    window["dailyBreakdown"] = data.breakdown;
    finalizePanel.style.display = "block";
    loadWeeklyData();
  } catch (error) {
    console.error("Confirm day error:", error);
    alert(error.message || "Failed to finalize daily log");
  }
}

// Event handler for "View Score Breakdown" button in the finalize panel.
function showDailyBreakdown() {
  if (!window["dailyBreakdown"] || window["dailyBreakdown"].length === 0) {
    alert(
      "No breakdown available for today's score. Try finalizing your daily log and waiting a few seconds."
    );
    return;
  }

  let tableHTML = `
    <table class="breakdown-table">
      <thead>
        <tr>
          <th>Nutrient</th>
          <th>Your Intake (g)</th>
          <th>Recommended Mean (g)</th>
          <th>Std Dev (g)</th>
          <th>Z Score</th>
          <th>Weight</th>
          <th>Score Contribution</th>
        </tr>
      </thead>
      <tbody>
  `;

  window["dailyBreakdown"].forEach((nutrient) => {
    tableHTML += `
      <tr>
        <td>${nutrient.nutrient_name}</td>
        <td>${
          nutrient.total_amount ? nutrient.total_amount.toFixed(2) : "N/A"
        }</td>
        <td>${
          nutrient.global_mean ? nutrient.global_mean.toFixed(2) : "N/A"
        }</td>
        <td>${nutrient.std_dev ? nutrient.std_dev.toFixed(2) : "N/A"}</td>
        <td>${nutrient.z_score ? nutrient.z_score.toFixed(2) : "N/A"}</td>
        <td>${nutrient.dii_score_per_unit.toFixed(4)}</td>
        <td>${
          nutrient.contribution ? nutrient.contribution.toFixed(2) : "N/A"
        }</td>
      </tr>
    `;
  });

  tableHTML += `
      </tbody>
    </table>
  `;

  const explanationHTML = `
    <p class="breakdown-explanation">
      <strong>Explanation:</strong> "Your Intake" is the total amount of the nutrient consumed today.
      "Recommended Mean" and "Std Dev" are the population reference values.
      The "Z Score" shows how far your intake deviates from the mean,
      "Weight" is the nutrient's inflammatory factor, and "Score Contribution" is the product of the Z Score and the Weight.
    </p>
  `;

  const modal = document.createElement("div");
  modal.className = "breakdown-modal";
  modal.innerHTML = `
    <div class="modal-content">
      <h3>Daily Score Breakdown</h3>
      ${tableHTML}
      ${explanationHTML}
      <button class="btn close-btn" onclick="this.closest('.breakdown-modal').remove()">Close</button>
    </div>
  `;

  document.body.appendChild(modal);
}

// Load Daily Data Function: Loads today's logged foods.
async function loadDailyData() {
  try {
    const response = await fetch("/daily_data");
    if (!response.ok) throw new Error("Failed to load daily data");
    const data = await response.json();
    diaryTable.innerHTML = "";
    data.forEach((item) => {
      const [id, foodName, quantity] = item;
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${foodName}</td>
        <td>${quantity}g</td>
        <td>
          <button class="btn breakdown-btn" data-entry-id="${id}" onclick="showBreakdown(${id})">
            View Breakdown
          </button>
          <button class="btn delete-btn" data-entry-id="${id}" onclick="deleteEntry(${id})">
            Delete
          </button>
        </td>
      `;
      diaryTable.appendChild(row);
    });
  } catch (error) {
    console.error("Daily data error:", error);
    alert("Failed to load daily entries");
  }
}

// Load Weekly Data Function: Updates the weekly trend graph.
async function loadWeeklyData() {
  try {
    const response = await fetch("/weekly_data");
    if (!response.ok) throw new Error("Failed to load weekly data");
    const data = await response.json();
    scoreChart.data.labels = data.dates;
    scoreChart.data.datasets[0].data = data.scores;
    scoreChart.update();
  } catch (error) {
    console.error("Weekly data error:", error);
    alert("Failed to load weekly trend");
  }
}

// Show Breakdown Modal for an individual food entry.
async function showBreakdown(entryId) {
  const id = Math.abs(parseInt(entryId));
  try {
    const response = await fetch(`/entry_breakdown/${id}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to load breakdown");
    }
    const data = await response.json();
    const breakdownHTML = data.breakdown
      ?.map((nutrient) => {
        return `
          <div class="breakdown-item">
            <span class="nutrient-name">${
              nutrient.nutrient_name || "Unknown"
            }</span>:
            <span class="nutrient-value">Inflammatory effect: ${nutrient.dii_score_per_unit.toFixed(
              4
            )}</span>
          </div>
        `;
      })
      .join("");
    const modal = document.createElement("div");
    modal.className = "breakdown-modal";
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Nutrient Breakdown for: ${data.food_name || "Unknown Food"}</h3>
        <div class="breakdown-list">${
          breakdownHTML || "No breakdown available"
        }</div>
        <button onclick="this.closest('.breakdown-modal').remove()">Close</button>
      </div>
    `;
    document.body.appendChild(modal);
  } catch (error) {
    console.error("Breakdown error:", error);
    alert(error.message || "Failed to load breakdown details");
  }
}

// Delete Entry Handler
async function deleteEntry(entryId) {
  if (!confirm("Are you sure you want to delete this entry?")) return;
  try {
    const response = await fetch(`/delete_entry/${entryId}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete entry");
    loadDailyData();
    loadWeeklyData();
  } catch (error) {
    console.error("Delete error:", error);
    alert("Failed to delete entry");
  }
}

// Logout Handler
async function logout() {
  try {
    await fetch("/logout");
    window.location.href = "/";
  } catch (error) {
    console.error("Logout error:", error);
    alert("Failed to logout");
  }
}

// Portion Guide Functionality
function showPortionGuide() {
  const portionGuideHTML = `
    <div class="modal-content">
      <h3>Portion Guide</h3>
      <div class="guide-section">
        <h4>Starchy Foods</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Food Type</th>
              <th>Portion Size (Original Unit)</th>
              <th>Equivalent (g)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Puffed or flaked breakfast cereal</td>
              <td>30g (1 oz) or 3 tablespoons</td>
              <td>30g</td>
            </tr>
            <tr>
              <td>Porridge oats or shredded cereal</td>
              <td>40g (1.4 oz) or 3 tablespoons</td>
              <td>40g</td>
            </tr>
            <tr>
              <td>Muesli or granola</td>
              <td>45g (1.6 oz) or 2–3 tablespoons</td>
              <td>45g</td>
            </tr>
            <tr>
              <td>Bread (or toast)</td>
              <td>34–36g (1.2–1.3 oz) per slice</td>
              <td>~35g per slice</td>
            </tr>
            <tr>
              <td>Baked potato (with skin)</td>
              <td>180g (6.3 oz)</td>
              <td>180g (1 medium potato)</td>
            </tr>
            <tr>
              <td>Boiled potatoes (with skin)</td>
              <td>175g (6.17 oz); e.g., 5–6 thumb‐sized or 3 egg‐sized</td>
              <td>175g</td>
            </tr>
            <tr>
              <td>Pasta (boiled)</td>
              <td>75g uncooked or 150g cooked</td>
              <td>75g uncooked / 150g cooked</td>
            </tr>
            <tr>
              <td>Rice (boiled)</td>
              <td>50g uncooked or 150g cooked</td>
              <td>50g uncooked / 150g cooked</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="guide-section">
        <h4>Non-Dairy Proteins</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Food Type</th>
              <th>Portion Size (Original Unit)</th>
              <th>Equivalent (g)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Cooked meat</td>
              <td>90g (deck of cards)</td>
              <td>90g</td>
            </tr>
            <tr>
              <td>Cooked fish</td>
              <td>140g (palm size)</td>
              <td>140g</td>
            </tr>
            <tr>
              <td>Eggs</td>
              <td>120g (2 medium eggs)</td>
              <td>120g</td>
            </tr>
            <tr>
              <td>Baked beans</td>
              <td>150g (4 tablespoons)</td>
              <td>150g</td>
            </tr>
            <tr>
              <td>Lentils or chickpeas</td>
              <td>150g (4 tablespoons)</td>
              <td>150g</td>
            </tr>
            <tr>
              <td>Tofu/soya or meat alternative</td>
              <td>100g (4 tablespoons)</td>
              <td>100g</td>
            </tr>
            <tr>
              <td>Unsalted nuts or nut butter</td>
              <td>30g (1 oz) or 1 tablespoon</td>
              <td>30g</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="guide-section">
        <h4>Dairy and Dairy-Free Alternatives</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Food Type</th>
              <th>Portion Size (Original Unit)</th>
              <th>Equivalent (g)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Milk</td>
              <td>200ml (1 glass)</td>
              <td>~200g</td>
            </tr>
            <tr>
              <td>Yoghurt or fortified soya yoghurt</td>
              <td>125ml (3 tablespoons)</td>
              <td>~125g</td>
            </tr>
            <tr>
              <td>Hard cheese</td>
              <td>30g (small matchbox)</td>
              <td>30g</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="guide-section">
        <h4>Fruit and Vegetables</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Food Type</th>
              <th>Portion Size (Original Unit)</th>
              <th>Equivalent (g)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Apple/Orange/Pear/Banana</td>
              <td>1 medium fruit</td>
              <td>~80g</td>
            </tr>
            <tr>
              <td>Kiwis/Apricots/Satsumas/Plums</td>
              <td>Approximately 2 fruits</td>
              <td>~80g total</td>
            </tr>
            <tr>
              <td>Dried fruit (e.g., raisins)</td>
              <td>1 tablespoon</td>
              <td>30g</td>
            </tr>
            <tr>
              <td>Berries</td>
              <td>15–20 berries</td>
              <td>~80g</td>
            </tr>
            <tr>
              <td>Grapes</td>
              <td>10–12 grapes</td>
              <td>~80g</td>
            </tr>
            <tr>
              <td>Peas/Sweetcorn/Carrots</td>
              <td>About 3 heaped tablespoons</td>
              <td>~80g</td>
            </tr>
            <tr>
              <td>Salad</td>
              <td>Roughly one cereal bowl</td>
              <td>~80g</td>
            </tr>
            <tr>
              <td>Cherry tomatoes</td>
              <td>Around 7 cherry tomatoes</td>
              <td>~80g</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="guide-section">
        <h4>Oils and Spreads</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Food Type</th>
              <th>Portion Size (Original Unit)</th>
              <th>Equivalent (g)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Oils and spreads</td>
              <td>Approximately 1 teaspoon</td>
              <td>~5g</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="source-note">
        <small>Source: <a href="https://www.bupa.co.uk/newsroom/ourviews/portion-size-guide" target="_blank">Bupa Portion Size Guide</a></small>
      </div>
      <button class="btn close-btn" onclick="document.getElementById('portionGuideModal').style.display='none'">Close</button>
    </div>
  `;
  const modal = document.getElementById("portionGuideModal");
  modal.innerHTML = portionGuideHTML;
  modal.style.display = "block";
}
