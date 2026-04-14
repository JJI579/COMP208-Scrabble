import asyncio
import json
from pathlib import Path

from .scrabble import Scrabble, Bot

BASE_DIR = Path(__file__).resolve()
PROJECT_ROOT = BASE_DIR.parents[2]

print("Loading words...")

word_file = PROJECT_ROOT / "sowpods.txt"

with open(word_file, "r", encoding="utf-8") as f:
    word_set = set(line.strip().upper() for line in f if line.strip())

print(f"Loaded {len(word_set)} words")

pointsData = json.load(open(PROJECT_ROOT / "scrabble_points.json"))
distributionArray = json.load(open(PROJECT_ROOT / "letter_distribution.json"))

# -----------------------------
# BOARD
# -----------------------------
defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]


# -----------------------------
# PATCH WORD CHECK
# -----------------------------
async def fake_check_word(self, word: str):
    return word.upper() in word_set

Scrabble.check_word = fake_check_word


# -----------------------------
# RUN GAME
# -----------------------------
async def run_game():
    game = Scrabble(arr)

    game.init_game([
        type("P", (), {"userID": 1})(),
        type("P", (), {"userID": 2})(),
    ])

    bots = {
        1: Bot(word_set),
        2: Bot(word_set)
    }

    scores = {1: 0, 2: 0}

    # Track distribution usage
    original_distribution = distributionArray.copy()
    letters_remaining = sum(1 for letter in original_distribution if letter != " ")  # Count non-blank letters

    turn = 0
    pass_streak = 0
    MAX_PASSES = 20  # Allow even more passes before stopping
    MAX_TURNS = 1000  # Allow more turns to use all letters

    while turn < MAX_TURNS and not game.finished and letters_remaining > 0:
        player_id = game.fetch_turn()
        bot = bots[player_id]

        bot.letters = game.fetch_player_letters(player_id)[:]

        print("\n====================")
        print(f"TURN {turn} | Player {player_id}")
        print("Letters:", bot.letters)

        move_found = False
        for attempt in range(5):  # retry up to 5 times
            move = await bot.choose_move(game)

            if not move:
                continue

            if not move or len(move) != 4:
                continue

            points, word, pos, direction = move
            direction = direction.lower()

            print(f"PLAY: {word} at {pos} {direction} for {points} points")

            try:
                result = await game._place_word(word, pos, direction.lower())
            except Exception as e:
                print("ERROR:", e)
                result = False

            print("RESULT:", result)

            if result:
                scores[player_id] += result
                # Remove used letters from bot's rack AND distribution count
                temp_letters = bot.letters.copy()
                for c in word:
                    if c in temp_letters:
                        temp_letters.remove(c)
                        # Decrement from remaining distribution count
                        letters_remaining -= 1
                
                # Set the player's letters to the remaining
                game.playerLetters[str(player_id)] = temp_letters[:]
                
                # Give new letters to top up to 7
                game.give_player_letters(player_id, 7 - len(temp_letters))
                
                # Update bot's letters
                bot.letters = game.fetch_player_letters(player_id)[:]
                
                print(f"  Letters remaining in distribution: {letters_remaining}")
                
                move_found = True
                break

        if not move_found:
            print("PASS (no valid moves after retries)")
            pass_streak += 1
            if pass_streak >= MAX_PASSES:
                print("\nStopping: too many passes")
                break
        else:
            pass_streak = 0

        game.next_turn()
        turn += 1

    print("\nFINAL SCORES:")
    for pid, score in scores.items():
        print(f"Player {pid}: {score} points")

    print(f"\nLetters remaining in distribution: {letters_remaining}")
    print(f"Letters used: {len(original_distribution) - letters_remaining} / {len(original_distribution)}")

    print("\nFINAL BOARD:\n")
    game.print_board()


if __name__ == "__main__":
    asyncio.run(run_game())