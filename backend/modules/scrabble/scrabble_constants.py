from pathlib import Path
import json

# Constants
BOARD_SIZE = 15
BOT_ID = -2
CENTER = (7,7)
EMPTY_TILE = "|"
POINTS_PATH = Path.cwd() / "scrabble_points.json"
POINTS_DATA = json.load(open(POINTS_PATH))
LETTER_BAG_PATH = Path.cwd() / "letter_distribution.json"