import numpy as np
import matplotlib.pyplot as plt

# Questions (labels) – match these to your dissertation headings
questions = [
    'Q1: Overall Satisfaction',
    'Q2: Ease of Navigation',
    'Q3: Clarity of Instructions',
    'Q4: Food Search & Logging',
    'Q5: Nutrient Breakdown',
    'Q6: Portion Guide Utility',
    'Q7: Weekly Trend Chart'
]

# Raw ratings from the table above – each sub-list corresponds to one question
ratings_data = [
    [4, 4, 4, 3, 4, 4, 4, 4],  # Q1
    [5, 3, 5, 3, 4, 3, 4, 3],  # Q2
    [2, 5, 3, 3, 3, 3, 3, 4],  # Q3
    [5, 5, 3, 5, 4, 4, 3, 3],  # Q4
    [4, 4, 4, 3, 4, 4, 4, 4],  # Q5
    [3, 4, 3, 5, 5, 3, 4, 4],  # Q6
    [4, 3, 5, 2, 4, 5, 4, 4]   # Q7
]

# Calculate the average for each question
averages = [np.mean(r) for r in ratings_data]

# Create the bar chart
plt.bar(questions, averages)

# Labeling
plt.ylabel('Average Rating (1–5)')
plt.title('User Feedback on the DII Tracker')
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 5)  # Ensure the y-axis goes from 0 to 5 for clarity
plt.tight_layout()  # Minimizes clipping of labels

# Show the plot
plt.show()
