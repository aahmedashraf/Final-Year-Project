// dashboard.js
document.addEventListener("DOMContentLoaded", () => {
  // Initialize chart and load data
  initializeChart();
  loadDailyData();
  loadWeeklyData();
});

// DOM Elements
const foodSearch = document.getElementById("foodSearch");
const foodSuggestions = document.getElementById("foodSuggestions");
const diaryTable = document.getElementById("diaryTable").querySelector("tbody");
const addFoodBtn = document.getElementById("addFoodBtn");
const logoutBtn = document.getElementById("logoutBtn");
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
      labels: [],
      datasets: [
        {
          label: "Weekly Inflammation Score",
          data: [],
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.2)",
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: "Inflammation Score",
          },
        },
        x: {
          title: {
            display: true,
            text: "Date",
          },
        },
      },
    },
  });
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
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        food_name: food,
        quantity: quantity,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to calculate score");
    }

    const result = await response.json();

    // Clear inputs
    foodSearch.value = "";
    document.getElementById("foodQuantity").value = "";
    addFoodBtn.disabled = true;

    // Refresh data
    loadDailyData();
    loadWeeklyData();
  } catch (error) {
    console.error("Add food error:", error);
    alert(error.message || "Failed to add food");
  }
}

// Load Daily Data
async function loadDailyData() {
  try {
    const response = await fetch("/daily_data");
    if (!response.ok) throw new Error("Failed to load daily data");

    const data = await response.json();
    diaryTable.innerHTML = "";

    data.forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${item[0]}</td>
                <td>${item[1]}g</td>
                <td>${item[2].toFixed(2)}</td>
            `;
      diaryTable.appendChild(row);
    });
  } catch (error) {
    console.error("Daily data error:", error);
    alert("Failed to load daily entries");
  }
}

// Load Weekly Data
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
