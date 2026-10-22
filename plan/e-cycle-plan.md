# E-Cycle — Smart E-Waste Management System — Build Plan

## Goal
A working, mobile-responsive full-stack website for a college engineering project that manages e-waste through collection requests, segregation, reuse/repair, and responsible recycling.

## Stack (to confirm)
- Frontend: HTML5, CSS3, JavaScript, Chart.js, Font Awesome
- Backend: Flask (Python) + SQLite (or deployable alternative)
- Deployment: local demo + optional online

## Pages
1. Home — hero, feature cards, circular-economy workflow, "why not household waste" section, footer
2. Dashboard — live stats, bar chart (requests by item type), doughnut chart (conditions), recent requests table, refresh
3. Submit E-Waste — validated form, unique request ID, success message + recommendation
4. Collection Requests — table with search/filter/sort, detail view, status update, delete (confirm), CSV export
5. Segregation Guide — educational cards + circular-economy principle + safety warnings
6. About Project — problem, objectives, solution, tech, future scope, editable group members

## Database
- Table `e_waste_requests`: id, request_id, submitted_at, full_name, contact, pickup_location, item_type, condition, quantity, notes, category, recommendation, status
- Auto-created on first launch; unique request IDs; persistent storage

## Segregation Engine (rule-based)
- Working → reuse / donation / refurbishment
- Repairable → repair first, else authorized recycling
- Damaged → safe handling + authorized facility
- Batteries → always separate special handling (never burn/crush/open)
- Chargers/cables → material recovery collection
- TVs/monitors → careful handling + authorized collection
- Store category + recommendation with every request

## Admin & Security
- Login with hashed passwords; protected routes for status update / delete
- Parameterized queries, input validation/sanitization, no secrets in frontend

## Testing (10 cases)
Submit working phone, repairable laptop, damaged battery; reject missing fields; reject zero/negative quantity; verify SQLite persistence; verify dashboard updates; verify filters/search; verify status persists; verify CSV export.

## Deliverables
- Full source code, requirements.txt, DB init code, README (setup + deploy), demo guide for teacher

## Build Steps
1. Scaffold Flask app + DB init + base template/CSS
2. Home page
3. Submit form + segregation engine
4. Dashboard + charts
5. Collection Requests management
6. Segregation Guide + About
7. Admin auth
8. Run the 10 test cases
9. README + demo guide