from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import random
import uuid

SUITS = ["DIAMONDS", "HEARTS", "CLUBS", "SPADES"]
RANKS = list(range(1, 14))  # Ace=1, 2..10, Jack=11, Queen=12, King=13

@dataclass(frozen=True)
class Card:
    suit: str
    rank: int

    def __str__(self):
        rank_name = {1: "A", 11: "J", 12: "Q", 13: "K"}.get(self.rank, str(self.rank))
        return f"{rank_name} of {self.suit.title()}"

def diamond_deck():
    return [Card("DIAMONDS", r) for r in RANKS]

def suit_deck(suit: str):
    assert suit in SUITS and suit != "DIAMONDS"
    return [Card(suit, r) for r in RANKS]


class Player:
    def __init__(self, name: str, suit: Optional[str] = None):
        self.name = name
        self.suit = suit
        self.hand: Dict[int, Card] = {}
        self.score: float = 0.0
        self.history: List[Tuple[Card, Optional[Card], float]] = []

    def assign_suit(self, suit: str):
        self.suit = suit
        self.hand = {c.rank: c for c in suit_deck(suit)}

    def available_ranks(self) -> List[int]:
        return sorted(self.hand.keys())

    def play(self, diamond: Card, context: Dict) -> Card:
        # Default random strategy; override in bots
        rank = random.choice(self.available_ranks())
        return self.hand.pop(rank)

    def observe_round_result(self, diamond: Card, played_card: Optional[Card], points_won: float, context: Dict):
        self.history.append((diamond, played_card, points_won))

    def __repr__(self):
        return f"Player({self.name}, suit={self.suit}, score={self.score:.2f}, cards={len(self.hand)})"

# ----- Game engine -----
class DiamondsGame:
    
    def __init__(self, players: List[Player], seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        if len(players) < 1 or len(players) > 3:
            raise ValueError("Players must be between 1 and 3 (HEARTS/CLUBS/SPADES).")

        available_suits = ["HEARTS", "CLUBS", "SPADES"]
        random.shuffle(available_suits)
        for p, s in zip(players, available_suits):
            p.assign_suit(s)

        self.players = players
        self.id = str(uuid.uuid4())
        self.state = "CREATED"
        self.round_index = 0
        self.diamonds = diamond_deck()
        random.shuffle(self.diamonds)
        self.history: List[Dict] = []

    def start(self):
        if self.state != "CREATED":
            raise RuntimeError("Game already started or finished.")
        self.state = "RUNNING"

    def step(self) -> bool:
        if self.state != "RUNNING":
            raise RuntimeError("Game is not running.")
        if self.round_index >= len(self.diamonds):
            self.state = "FINISHED"
            return False

        diamond = self.diamonds[self.round_index]
        ctx = {"round": self.round_index + 1, "remaining_rounds": len(self.diamonds) - self.round_index}
        bids: Dict[str, Card] = {}
        for p in self.players:
            bids[p.name] = p.play(diamond, ctx)

        max_rank = max(card.rank for card in bids.values())
        winners = [name for name, card in bids.items() if card.rank == max_rank]
        points_each = diamond.rank / len(winners)

        for p in self.players:
            gained = points_each if p.name in winners else 0.0
            p.score += gained
            p.observe_round_result(diamond, bids[p.name], gained, ctx)

        self.history.append({
            "round": self.round_index + 1,
            "diamond": diamond.rank,
            "bids": {name: card.rank for name, card in bids.items()},
            "winners": winners,
            "points_each": points_each,
        })
        self.round_index += 1

        if self.round_index >= len(self.diamonds):
            self.state = "FINISHED"
            return False
        return True

    def run_to_end(self):
        if self.state == "CREATED":
            self.start()
        while self.state == "RUNNING":
            self.step()

    def abandon(self):
        if self.state not in ("FINISHED", "ABANDONED"):
            self.state = "ABANDONED"

    
    def game_status(self) -> Dict:
        return {
            "game_id": self.id,
            "state": self.state,
            "round": self.round_index,
            "players": [{"name": p.name, "suit": p.suit, "score": p.score} for p in self.players],
        }

    def player_status(self, requester: str, reveal_all: bool = False) -> Dict[str, Dict]:
        out = {}
        for p in self.players:
            if reveal_all or p.name == requester:
                out[p.name] = {"suit": p.suit, "score": p.score, "available_ranks": p.available_ranks(), "cards_left": len(p.hand)}
            else:
                out[p.name] = {"suit": p.suit, "score": p.score, "available_ranks": None, "cards_left": len(p.hand)}
        return out

    def result(self) -> Dict:
        if self.state != "FINISHED":
            raise RuntimeError("Game not finished yet.")
        standings = sorted(((p.name, p.score) for p in self.players), key=lambda x: x[1], reverse=True)
        return {"game_id": self.id, "final_scores": standings, "history": list(self.history)}


class GameManager:
    def __init__(self):
        self.games: Dict[str, DiamondsGame] = {}

    def create_game(self, players: List[Player], seed: Optional[int] = None) -> str:
        game = DiamondsGame(players, seed=seed)
        self.games[game.id] = game
        return game.id

    def start_game(self, game_id: str):
        self.games[game_id].start()

    def step_game(self, game_id: str) -> bool:
        return self.games[game_id].step()

    def run_to_end(self, game_id: str):
        self.games[game_id].run_to_end()

    def game_status(self, game_id: str) -> Dict:
        return self.games[game_id].game_status()

    def player_status(self, game_id: str, requester: str, reveal_all: bool = False) -> Dict[str, Dict]:
        return self.games[game_id].player_status(requester, reveal_all=reveal_all)

    def abandon_game(self, game_id: str):
        self.games[game_id].abandon()

    def result(self, game_id: str) -> Dict:
        return self.games[game_id].result()
