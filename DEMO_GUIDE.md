# E-Cycle — Demonstration Guide (for a college teacher)

Follow this 5-minute script to show the project working end to end.

## 1. Start the app

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## 2. Home page

- Point out the hero, tagline, feature cards, and the circular-economy workflow.
- Mention the "why not the household bin" section.

## 3. Submit E-Waste (3 quick demos)

Go to **Submit E-Waste** and submit:

1. **Working Mobile Phone, quantity 1** → shows "Reusable" recommendation.
2. **Repairable Laptop** → shows "Repairable" recommendation.
3. **Damaged Battery** → shows "Special Handling" recommendation.

Each submission shows a unique Request ID (e.g. `EC-20261022-A1B2C3`).

## 4. Dashboard

- Show the statistics cards updating after each submission.
- Show the bar chart (requests by item type) and doughnut chart (conditions).
- Click **Refresh** to reload.

## 5. Collection Requests

- Show search (by Request ID or name), filters (item type, condition, status), and sorting.
- Click the eye icon to view full details.
- Log in as admin (`admin` / `admin123`) to show status update and delete (with confirmation).
- Click **Export CSV** to download the list.

## 6. Segregation Guide & About

- Show the four handling categories and the safety warnings.
- Show the About page (problem, objectives, solution, tech, future scope, group members).

## 7. Validation checks (optional)

- Try submitting an empty form → shows clear error messages.
- Try quantity 0 or negative → rejected.

## Key talking points

- Demonstrates the **circular economy**: Reduce → Reuse → Repair → Refurbish → Recycle → Recover Materials.
- The segregation engine is **rule-based** (explain the 6 rules), not machine learning.
- Data is stored persistently in SQLite and drives all statistics and charts.