class Player:
    def get_hand(self) -> list[int]:
        """Return a list of indexes where the hand is True."""
        result = [i for i, v in enumerate(self.hand) if v] + [
            f"+{i}" for i in self.additive_modifier
        ]
        if self.additive_modifier:
            result += ["*2"]
        return result

    """Represents a player with a 13-position boolean hand.

    - `hand` is a list of 13 booleans, all initialized to False.
    - `add_card(index)` marks the given position as True.
    - `reset_hand()` sets all positions back to False.
    """

    HAND_SIZE = 13

    def __init__(self) -> None:
        self.hand: list[bool] = [False] * self.HAND_SIZE
        self.additive_modifier: list[int] = []  # starts empty, can contain numbers
        self.multiplicative_modifier: bool = False  # flag, default False
        self.second_Chance: bool = False  # flag, default False

    def add_card(self, index) -> None:
        """Mark the given position as True or add to additive_modifier.

        Args:
            index: Zero-based position in the hand (0..12), or string '+N'.

        Raises:
            ValueError: If index is out of range or already set, or invalid modifier.
        """
        if isinstance(index, str):
            if index == "Second Chance":
                self.second_Chance = True
                return
            if index.startswith("+"):
                try:
                    num = int(index[1:])
                    self.additive_modifier.append(num)
                except ValueError:
                    raise ValueError(f"Invalid additive modifier: {index}")
                return
            if index.startswith("*"):
                self.multiplicative_modifier = True
                return
        if not 0 <= index < self.HAND_SIZE:
            raise ValueError(f"index must be between 0 and {self.HAND_SIZE - 1}")
        if self.hand[index]:
            if self.second_Chance:
                self.second_Chance = False
                return
            raise IndexError(f"position {index} is already True")
        self.hand[index] = True
        # If adding this card results in exactly 7 True positions, add +15 and end the round
        if sum(self.hand) == 7:
            self.additive_modifier.append(15)
            raise IndexError("Reached 7 True positions")

    def reset_hand(self) -> None:
        """Reset all positions and modifiers to initial state."""
        for i in range(self.HAND_SIZE):
            self.hand[i] = False
        self.additive_modifier = []
        self.multiplicative_modifier = False
        self.second_Chance = False

    def Score(self) -> int:
        """Return the sum of zero-based positions that are True, plus additive modifiers.

        If multiplicative_modifier is True, multiply the hand sum by 2.

        Example: if positions 0, 5, and 12 are True, additive_modifier=[2,4], and multiplicative_modifier=True,
        the score is (0+5+12)*2+2+4=46.
        """
        hand_sum = sum(i for i, v in enumerate(self.hand) if v)
        if self.multiplicative_modifier:
            hand_sum *= 2
        return hand_sum + sum(self.additive_modifier)


__all__ = ["Player"]
