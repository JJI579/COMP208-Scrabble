import asyncio
import json
from pathlib import Path

from .scrabble import Scrabble, Bot

# Bot.isWord = Bot.is_word

# -----------------------------
# LOAD DATA
# -----------------------------
BASE_DIR = Path(__file__).resolve()
PROJECT_ROOT = BASE_DIR.parents[2]

print("Loading words...")

word_file = PROJECT_ROOT / "sowpods.txt"

with open(word_file, "r", encoding="utf-8") as f:
    word_set = set(line.strip().upper() for line in f if line.strip())

pointsData = json.load(open(PROJECT_ROOT / "scrabble_points.json"))
distributionArray = json.load(open(PROJECT_ROOT / "letter_distribution.json"))

print(f"Loaded {len(word_set)} words")

# -----------------------------
# FORCE SOWPODS VALIDATION ONLY
# -----------------------------
async def fake_check_word(self, word: str):
    return word.upper() in word_set

Scrabble.check_word = fake_check_word

# -----------------------------
# BOARD
# -----------------------------
defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

# -----------------------------
# BOT PATCH (scoring stub)
# -----------------------------
def sim_place_word_stub(self, word, pos, direction):
    return len(word)

Bot.sim_place_word = sim_place_word_stub

# -----------------------------
# PREVENT BOT REPEATING BAD MOVES
# -----------------------------
def patch_bot_memory(bot):
    bot.forbidden_words = set()

original_choose_move = Bot.choose_move

def patched_choose_move(self, scrabble):
    move = original_choose_move(self, scrabble)

    if not move:
        return None

    word, pos, direction = move

    if hasattr(self, "forbidden_words") and word in self.forbidden_words:
        return None

    return move

Bot.choose_move = patched_choose_move


# -----------------------------
# GAME LOOP
# -----------------------------
async def run_game():
    game = Scrabble(arr)

    game.init_game([
        type("P", (), {"userID": 1})(),
        type("P", (), {"userID": 2})(),
    ])

    game.give_player_letters(1, 7)
    game.give_player_letters(2, 7)

    bot1 = Bot(word_set)
    bot2 = Bot(word_set)


    bots = {1: bot1, 2: bot2}

    bot1.letters = game.fetch_player_letters(1)
    bot2.letters = game.fetch_player_letters(2)

    turn = 0
    pass_streak = 0
    MAX_PASSES = 10
    MAX_TURNS = 300

    while turn < MAX_TURNS:
        player_id = game.fetch_turn()
        bot = bots[player_id]

        print("\n====================")
        print(f"TURN {turn} | Player {player_id}")
        print("Letters:", bot.letters)

        move = bot.choose_move(self)

        if not move:
            print("PASS")
            pass_streak += 1
            game.next_turn()
            turn += 1

            if pass_streak >= MAX_PASSES:
                print("\nStopping: too many passes")
                break
            continue

        pass_streak = 0

        word, pos, direction = move
        print(f"PLAY: {word} at {pos} {direction}")

        try:
            result = await game._place_word(word, pos, direction)
        except Exception as e:
            print("ERROR:", e)
            result = False

        print("RESULT:", result)

        if result:
            for c in word:
                if c in bot.letters:
                    bot.letters.remove(c)

            game.give_player_letters(player_id, 7 - len(bot.letters))
            bot.letters = game.fetch_player_letters(player_id)
        else:
            # IMPORTANT: stop retrying failed words
            bot.forbidden_words.add(word)

        game.next_turn()
        turn += 1

    print("\nFINAL BOARD:\n")
    game.print_board()


if __name__ == "__main__":
    asyncio.run(run_game())