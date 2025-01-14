document.getElementById("addFoodBtn").addEventListener("click", addFoodToDiary);

const foodSearch = document.getElementById("foodSearch");
const foodSuggestions = document.getElementById("foodSuggestions");
const diaryTable = document.getElementById("diaryTable").querySelector("tbody");
const scoreText = document.getElementById("scoreText");
const addFoodBtn = document.getElementById("addFoodBtn");
let totalInflammationScore = 0;
let selectedFood = null;

// Data for Chart.js
const foodItems = [];
const scoreTrend = [];

// Initialize Chart.js
const ctx = document.getElementById("scoreChart").getContext("2d");
const scoreChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [], // Food item labels
    datasets: [
      {
        label: "Inflammation Score Trend",
        data: [], // Score data
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
        fill: true,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Inflammation Score",
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.raw;
            return value > 0
              ? `${value.toFixed(2)} (Pro-inflammatory)`
              : `${value.toFixed(2)} (Anti-inflammatory)`;
          },
        },
      },
    },
  },
});

// Fetch food suggestions from USDA API
foodSearch.addEventListener("input", async () => {
  const query = foodSearch.value.trim();
  foodSuggestions.innerHTML = ""; // Clear previous suggestions

  if (query.length < 3) return; // Wait until user types at least 3 characters

  try {
    const response = await fetch(
      `https://api.nal.usda.gov/fdc/v1/foods/search?query=${query}&dataType=Foundation&api_key=sns0HxXgofxkqaeFcYRUpPzxcxoN7wy62Mf2Aq85`
    );
    const data = await response.json();

    if (data.foods && data.foods.length > 0) {
      data.foods.forEach((food) => {
        const li = document.createElement("li");
        li.textContent = food.description;
        li.dataset.fdcId = food.fdcId;
        foodSuggestions.appendChild(li);
      });
    }
  } catch (error) {
    console.error("Error fetching food suggestions:", error);
  }
});

// Select a food item from suggestions
foodSuggestions.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    foodSearch.value = e.target.textContent;
    selectedFood = e.target.dataset.fdcId;
    foodSuggestions.innerHTML = ""; // Clear suggestions
    addFoodBtn.disabled = false; // Enable Add button
  }
});

// Add selected food to the diary
async function addFoodToDiary() {
  const food = document.getElementById("foodSearch").value.trim();
  const quantity = parseFloat(document.getElementById("foodQuantity").value);

  // Validate input
  if (!food) {
    alert("Please enter a food name.");
    return;
  }
  if (isNaN(quantity) || quantity <= 0) {
    alert("Please enter a valid quantity greater than 0.");
    return;
  }

  try {
    // Send request to /calculate endpoint
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

    if (response.ok) {
      const data = await response.json();
      console.log("Response from /calculate:", data);

      // Check if the DII score is returned
      if (data.dii_score !== undefined) {
        const foodScore = data.dii_score;

        // Add food item to diary table
        const diaryTable = document.getElementById("diaryTable");
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${data.food_name}</td>
          <td>${quantity} g</td>
          <td>${foodScore.toFixed(2)}</td>
        `;
        diaryTable.appendChild(row);

        // Update total inflammation score
        totalInflammationScore += foodScore;

        // Update graph and visual representation
        foodItems.push(data.food_name);
        scoreTrend.push(totalInflammationScore);
        updateChart();
        updateScore();
      } else {
        alert("Failed to calculate DII score. Please try again.");
      }
    } else {
      const error = await response.json();
      alert(error.error || "An error occurred while calculating the score.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while adding the food to the diary.");
  }
}

function updateScore() {
  scoreText.textContent = totalInflammationScore.toFixed(2);
}

function updateChart() {
  scoreChart.data.labels = foodItems;
  scoreChart.data.datasets[0].data = scoreTrend;
  scoreChart.update();
}
