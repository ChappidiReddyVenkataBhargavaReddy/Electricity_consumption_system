# Electricity Consumption Analysis System

Flask project for consumer/meter management, cumulative readings, kWh usage reports, high-usage detection, charts and validation.

## Run on Windows / VS Code
1. Open this folder in VS Code.
2. `py -m venv .venv`
3. `.\.venv\Scripts\Activate.ps1`
4. `python -m pip install -r requirements.txt`
5. `python app.py`
6. Open http://127.0.0.1:5000 in Chrome.

If activation is blocked, run:
` .\.venv\Scripts\python.exe -m pip install -r requirements.txt`
then ` .\.venv\Scripts\python.exe app.py`

## Features
- Consumer, meter and dated meter-reading records.
- Monthly/yearly consumption and configurable high-use threshold (default 300 kWh/month).
- Reading validation: chronological dates; lower cumulative values flagged as possible reset/rollover.
- Demo sample records are inserted on first launch.
- SQLite is used by default to keep local setup simple. `database/schema.sql` provides the suggested MySQL table design.

## Calculation assumptions
Consumption = current cumulative kWh - previous cumulative kWh for the same meter. The interval is attributed to the month/year of the ending reading. Negative differences are flagged and excluded; rollover amounts are not guessed. These estimates do not replace official billing.

## Optional data-analysis stack
Install `python -m pip install -r requirements-analysis.txt` to add Pandas, NumPy and Matplotlib where supported. The web app does not require them because some Windows security policies block native extensions.

## Push to your private GitHub repository
`git init`
`git add .`
`git commit -m "Initial electricity consumption analysis system"`
`git branch -M main`
`git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git`
`git push -u origin main`

If origin already exists: `git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git`

Do not commit `.venv`, `.env`, passwords, or database credentials.
