# F1 Race Engineering

Desktop application in Python for Formula 1 telemetry analysis, strategy visualization, and machine learning dataset preparation.

## Milestone 1
- Project setup
- Qt main window
- Base tabs: Weekend / Strategy / ML Lab
- Abstract data providers
- FastF1 provider
- OpenF1 provider
- Cache manager
- Logging and config

## Setup

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
python -m ui.main