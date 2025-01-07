document.getElementById("addFoodBtn").addEventListener("click", addFoodToDiary);

const diaryTable = document.getElementById("diaryTable").querySelector("tbody");
const scoreText = document.getElementById("scoreText");
let totalInflammationScore = 0;

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

async function addFoodToDiary() {
  const food = document.getElementById("foodSearch").value.trim();
  const quantity = parseFloat(document.getElementById("foodQuantity").value);

  if (food && quantity > 0) {
    try {
      const response = await fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ food_name: food, quantity }),
      });

      if (response.ok) {
        const data = await response.json();
        const foodScore = data.dii_score;

        // Update total score
        totalInflammationScore += foodScore;

        // Add food to diary table
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${food}</td>
          <td>${quantity} g</td>
          <td>${foodScore.toFixed(2)}</td>
        `;
        diaryTable.appendChild(row);

        // Update score trend and graph
        foodItems.push(food);
        scoreTrend.push(totalInflammationScore);
        updateChart();

        // Update visual score
        updateScore();
      } else {
        const error = await response.json();
        alert(error.error || "Error calculating the score.");
      }
    } catch (error) {
      alert("An error occurred while communicating with the server.");
    }
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
