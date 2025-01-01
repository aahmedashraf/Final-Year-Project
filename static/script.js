document.getElementById("addFoodBtn").addEventListener("click", addFoodToDiary);

const diaryTable = document.getElementById("diaryTable").querySelector("tbody");
const scoreText = document.getElementById("scoreText");
let totalInflammationScore = 0;

async function addFoodToDiary() {
  const food = document.getElementById("foodSearch").value.trim();
  const quantity = document.getElementById("foodQuantity").value.trim();

  if (food && quantity) {
    try {
      // Make API call to calculate the score
      const response = await fetch("/calculate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          food_name: food,
          quantity: parseFloat(quantity),
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Update total inflammation score
        totalInflammationScore += data.dii_score;

        // Add food to diary table
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${food}</td>
          <td>${quantity} g</td>
          <td>${data.dii_score.toFixed(2)}</td>
        `;
        diaryTable.appendChild(row);

        // Update visual inflammation score
        updateInflammationScore();
      } else {
        const error = await response.json();
        alert(error.error);
      }
    } catch (err) {
      alert("Error communicating with the server.");
    }
  }
}

function updateInflammationScore() {
  scoreText.textContent = totalInflammationScore.toFixed(2);
}
