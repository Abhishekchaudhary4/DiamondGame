
import random
from diamonds.core import GameManager
from diamonds.bots import (
    HumanPlayer,
    RandomBot,
    MirrorBot,
    ThresholdBot,
    ConservativeBot,
    MirrorAndBluffBot,
)

BOT_LIST = [RandomBot, MirrorBot, ThresholdBot, ConservativeBot, MirrorAndBluffBot]

def choose_bot_by_number():
    print("\nAvailable bots:")
    for i, b in enumerate(BOT_LIST, 1):
        print(f"{i}. {b.__name__}")
    a_idx = int(input("Choose Bot A (enter number): ").strip()) - 1
    b_idx = int(input("Choose Bot B (enter number): ").strip()) - 1
    return BOT_LIST[a_idx], BOT_LIST[b_idx]

def main():
    print("Diamond Auction Game — Menu")
    print("1. Human vs Bot")
    print("2. Bot vs Bot (interactive selection)")
    mode = input("Enter 1 or 2: ").strip()

    gm = GameManager()
    if mode == "1":
        chosen_bot = random.choice(BOT_LIST)
        print(f"\nYou will play against: {chosen_bot.__name__}")
        gid = gm.create_game([HumanPlayer("You"), chosen_bot("Bot")])
        gm.start_game(gid)
        while gm.step_game(gid):
            pass
        print("\nFinal Result:")
        print(gm.result(gid))

    elif mode == "2":
        A, B = choose_bot_by_number()
        print(f"\nRunning: {A.__name__} vs {B.__name__}")
        gid = gm.create_game([A("BotA"), B("BotB")])
        gm.start_game(gid)
        gm.run_to_end(gid)
        print("\nFinal Result:")
        print(gm.result(gid))

    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()