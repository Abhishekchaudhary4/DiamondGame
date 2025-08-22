import random
from typing import Dict, Optional
from .core import Player, Card


class RandomBot(Player):
    def play(self, diamond: Card, context: Dict) -> Card:
        rank = random.choice(self.available_ranks())
        return self.hand.pop(rank)

class MirrorBot(Player):
    
    def play(self, diamond: Card, context: Dict) -> Card:
        if diamond.rank in self.hand:
            return self.hand.pop(diamond.rank)
        rank = random.choice(self.available_ranks())
        return self.hand.pop(rank)

class ThresholdBot(Player):
    
    def play(self, diamond: Card, context: Dict) -> Card:
        ranks = self.available_ranks()
        higher_or_equal = [r for r in ranks if r >= diamond.rank]
        if higher_or_equal:
            r = min(higher_or_equal)
        else:
            r = min(ranks)
        return self.hand.pop(r)

class ConservativeBot(Player):
   
    def play(self, diamond: Card, context: Dict) -> Card:
        r = min(self.available_ranks())
        return self.hand.pop(r)

class MirrorAndBluffBot(Player):
    
    def play(self, diamond: Card, context: Dict) -> Card:
        if diamond.rank in self.hand:
            # 30% chance to bluff instead of mirror
            if random.random() < 0.3:
                rank = random.choice(self.available_ranks())
                return self.hand.pop(rank)
            return self.hand.pop(diamond.rank)
        rank = random.choice(self.available_ranks())
        return self.hand.pop(rank)


class HumanPlayer(Player):
    
    def play(self, diamond: Card, context: Dict) -> Card:
        print(f"\nDiamond up: {diamond} (worth {diamond.rank})")
        print(f"Your cards: {self.available_ranks()}")
        while True:
            try:
                choice = int(input("Choose a card to play (rank number): ").strip())
                if choice in self.hand:
                    return self.hand.pop(choice)
                else:
                    print("Invalid selection — not in your hand. Try again.")
            except ValueError:
                print("Please enter a valid integer rank from your cards.")
