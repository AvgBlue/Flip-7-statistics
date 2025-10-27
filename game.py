from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import random
from player import Player


@dataclass
class ExperimentResults:
    running_avg: List[float]
    scores: List[int]
    count_reached7: int
    count_already_true: int
    cards_at_scoring: List[int]


def run_experiment(
    hands: int = 100_000, seed: Optional[int] = None
) -> ExperimentResults:
    if seed is not None:
        random.seed(seed)

    deck: List[int | str] = [0]
    for i in range(1, 13):
        deck += [i] * i
    deck += ["+2", "+4", "+6", "+8", "+10"] + ["*2"] + ["Second Chance"] * 3
    random.shuffle(deck)

    player = Player()
    len_deck = len(deck)
    index = 0
    scores: List[int] = []
    cards_at_scoring: List[int] = []
    running_avg: List[float] = []
    cumulative_sum = 0
    count_reached7 = 0
    count_already_true = 0

    remaining = hands
    while remaining > 0:
        if index == len_deck:
            index = 0
            random.shuffle(deck)
        try:
            player.add_card(deck[index])
        except IndexError as e:
            msg = str(e)
            if msg == "Reached 7 True positions":
                count_reached7 += 1
            elif msg.startswith("position ") and msg.endswith(" is already True"):
                count_already_true += 1

            cards_in_hand_now = sum(1 for v in player.hand if v)
            score = player.Score()
            scores.append(score)
            cards_at_scoring.append(cards_in_hand_now)
            cumulative_sum += score
            running_avg.append(cumulative_sum / len(scores))
            player.reset_hand()
            remaining -= 1
        except Exception as e:
            print(e)
        index += 1

    return ExperimentResults(
        running_avg=running_avg,
        scores=scores,
        count_reached7=count_reached7,
        count_already_true=count_already_true,
        cards_at_scoring=cards_at_scoring,
    )


__all__ = ["ExperimentResults", "run_experiment"]
