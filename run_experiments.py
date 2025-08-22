import random
import pandas as pd
import matplotlib.pyplot as plt
from diamonds.bots import RandomBot, MirrorBot, ThresholdBot, ConservativeBot, MirrorAndBluffBot
from diamonds.core import GameManager

def play_matchup(botA_cls, botB_cls, n_games=100, seed_base=0):
    rows = []
    for i in range(n_games):
        random.seed(seed_base + i)
        gm = GameManager()
        players = [botA_cls("BotA"), botB_cls("BotB")]
        gid = gm.create_game(players)
        gm.run_to_end(gid)
        res = gm.result(gid)
        scores = dict(res["final_scores"])
        rows.append({
            "game": i,
            "BotA": botA_cls.__name__,
            "BotB": botB_cls.__name__,
            "score_A": scores["BotA"],
            "score_B": scores["BotB"],
            "winner": "A" if scores["BotA"] > scores["BotB"] else ("B" if scores["BotB"] > scores["BotA"] else "TIE")
        })
    return pd.DataFrame(rows)

def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["BotA", "BotB"])
    out = grouped.agg(
        games=("game", "count"),
        win_rate_A=("winner", lambda s: (s == "A").mean()),
        win_rate_B=("winner", lambda s: (s == "B").mean()),
        tie_rate=("winner", lambda s: (s == "TIE").mean()),
        mean_score_A=("score_A", "mean"),
        mean_score_B=("score_B", "mean"),
        std_score_A=("score_A", "std"),
        std_score_B=("score_B", "std"),
    ).reset_index()
    return out

def run_all():
    matchups = [
        (RandomBot, MirrorBot),
        (RandomBot, ThresholdBot),
        (RandomBot, ConservativeBot),
        (RandomBot, MirrorAndBluffBot),
        (MirrorBot, MirrorAndBluffBot),
    ]
    all_dfs = []
    for idx, (A, B) in enumerate(matchups):
        print(f"Running {A.__name__} vs {B.__name__} (100 games)...")
        df = play_matchup(A, B, n_games=100, seed_base=1000 + idx * 100)
        csv_name = f"results_{A.__name__}_vs_{B.__name__}.csv"
        df.to_csv(csv_name, index=False)
        print(f"Saved {csv_name}")

        # Histogram of score difference
        diff = df["score_A"] - df["score_B"]
        plt.figure()
        plt.hist(diff, bins=20)
        plt.title(f"{A.__name__} (A) vs {B.__name__} (B): Score Difference")
        plt.xlabel("Score difference (A - B)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(f"hist_{A.__name__}_vs_{B.__name__}.png")
        plt.close()

        # Boxplot
        plt.figure()
        plt.boxplot([df["score_A"], df["score_B"]], labels=["BotA", "BotB"])
        plt.title(f"Scores: {A.__name__} vs {B.__name__}")
        plt.ylabel("Score")
        plt.tight_layout()
        plt.savefig(f"box_{A.__name__}_vs_{B.__name__}.png")
        plt.close()

        all_dfs.append(descriptive_stats(df))

    summary = pd.concat(all_dfs, ignore_index=True)
    summary.to_csv("results_summary.csv", index=False)
    print("Saved results_summary.csv")

if __name__ == "__main__":
    run_all()
