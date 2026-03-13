# F1 Race Engineering

Desktop application in Python for Formula 1 telemetry analysis, strategy visualization, and machine learning dataset preparation.

## Project Status

The project is currently in **Milestone 1**

Implemented so far:

- project setup with `pyproject.toml`
- Python virtual environment workflow
- Qt desktop application foundation with PySide6
- base tabs: `Weekend`, `Strategy`, `ML Lab`
- abstract provider interface
- `FastF1Provider`
- `OpenF1Provider`
- `CacheManager`
- basic logging configuration

## Tech Stack

- **Python**
- **PySide6** for the desktop UI
- **Qt Designer** for UI prototyping and layout design
- **pyqtgraph** for high-performance telemetry plots
- **matplotlib** for analytical and report-oriented charts
- **pandas** and **numpy** for data handling
- **FastF1** and **OpenF1** as data sources
- **Parquet** for local cache persistence

## Current Project Structure

```text
f1-race-engineering/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── config/
│   └── logging_config.py
│
├── cache/
│   ├── raw/
│   ├── normalized/
│   └── features/
│
├── data/
│   ├── __init__.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── cache_manager.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       ├── fastf1_provider.py
│       └── openf1_provider.py
│
├── ui/
│   ├── __init__.py
│   ├── main.py
│   ├── app.py
│   └── windows/
│       ├── __init__.py
│       └── main_window.py
│
└── tests/
    ├── __init__.py
    └── test_cache_manager.py
```

## Setup

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
python -m ui.main
```


## Milestones

### Milestone 1 — Foundation
- Project setup
- Qt main window
- Base tabs: Weekend / Strategy / ML Lab
- Abstract data providers
- FastF1 provider
- OpenF1 provider
- Cache manager
- Logging and config

### Milestone 2 — Weekend Explorer
- season / GP / session selection
- session metadata loading
- laps table
- first telemetry speed plot
- support for driver comparison
- lap selection

### Milestone 3 — Strategy Analysis
- stint extraction
- tire strategy Gantt chart
- pace by stint
- filtering of in-laps, out-laps, SC and VSC laps
- strategy summary

### Milestone 4 — Canonical Data Model
- source-independent normalized schema
- raw / normalized / features separation
- metadata tracking
- reusable repositories

### Milestone 5 — ML Preprocessing
- clean datasets
- era-aware dataset split
- feature engineering
- lap time prediction dataset
- tyre degradation dataset

### Milestone 6 — Baseline Machine Learning
- baseline regression models
- evaluation by circuit and era
- saved models
- feature importance

### Milestone 7 — Polish
- dark theme
- improved UX
- export tools
- saved analysis sessions
- packaging
- stronger test coverage

## Notes

This repository is being developed incrementally, with each milestone focused on keeping the architecture modular, readable, and maintainable.

The long-term objective is not just to build a dashboard, but a desktop race engineering analysis station with a clean data pipeline for future machine learning workflows.
