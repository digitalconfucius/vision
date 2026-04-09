"""Paths and constants."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
RAW_DIR = ROOT_DIR / "raw"
DB_PATH = ROOT_DIR / "wiki.db"

# Folder display metadata (icon, accent). Any folder not listed gets a default.
FOLDER_META = {
    "projects": {"icon": "▣", "accent": "#7aa2f7", "label": "Projects"},
    "infra": {"icon": "▤", "accent": "#9ece6a", "label": "Infrastructure"},
    "apis": {"icon": "▧", "accent": "#bb9af7", "label": "APIs"},
    "reference": {"icon": "▥", "accent": "#e0af68", "label": "Reference"},
    "people": {"icon": "▨", "accent": "#f7768e", "label": "People"},
    "ideas": {"icon": "▪", "accent": "#7dcfff", "label": "Ideas"},
}
DEFAULT_FOLDER_ACCENT = "#c0caf5"
