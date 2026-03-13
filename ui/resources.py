from __future__ import annotations


TEAM_COLORS = {
    "Red Bull Racing": "#1E41FF",
    "Ferrari": "#DC0000",
    "Mercedes": "#00D2BE",
    "McLaren": "#FF8700",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Williams": "#005AFF",
    "RB": "#1E5BC6",
    "AlphaTauri": "#2B4562",
    "Visa Cash App RB": "#1E5BC6",
    "Kick Sauber": "#00E701",
    "Sauber": "#00E701",
    "Alfa Romeo": "#900000",
    "Haas F1 Team": "#B6BABD",
    "Haas": "#B6BABD",
}

def get_team_color(team_name: str | None) -> str:
    if not team_name:
        return "#FFFFFF"
    
    return TEAM_COLORS.get(team_name, "#FFFFFF")