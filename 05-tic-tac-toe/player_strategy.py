"""
Player move strategies for Tic-Tac-Toe.

Your job: implement the Strategy pattern for move selection.
- The strategy decides WHERE a player places their piece
- This is how you swap between human input, random AI, and smart AI

Think about trade-offs:
- Random is fast but dumb
- Minimax is optimal but slow for larger boards
- How would you add a "difficulty level" strategy?
"""

from abc import ABC, abstractmethod
from models import Board


class MoveStrategy(ABC):
    """Abstract strategy — picks the next move given a board state."""

    @abstractmethod
    def get_move(self, board: Board) -> tuple[int, int]:
        """
        Decide where to place the next piece.

        Args:
            board: the current board state

        Returns:
            A (row, col) tuple for the chosen move.

        The returned position MUST be an empty cell.
        """
        ...


class RandomStrategy(MoveStrategy):
    """
    Picks a random empty cell on the board.

    Simple but useful for testing and as a baseline opponent.
    """

    def get_move(self, board: Board) -> tuple[int, int]:
        """Pick a random available move."""
        # TODO:
        # 1. Get the list of empty cells from the board
        # 2. Pick one at random
        # 3. Return it as (row, col)
        pass


# STRETCH: Implement MinimaxStrategy
#
# class MinimaxStrategy(MoveStrategy):
#     """
#     Uses the minimax algorithm to pick the optimal move.
#     Never loses — will always win or draw.
#
#     Think about:
#     - How do you score terminal states? (win=+10, loss=-10, draw=0)
#     - How do you alternate between maximizing and minimizing?
#     - How could you add alpha-beta pruning for efficiency?
#     """
#
#     def __init__(self, piece: Piece, opponent_piece: Piece):
#         # TODO: store which piece this strategy is playing as
#         pass
#
#     def get_move(self, board: Board) -> tuple[int, int]:
#         # TODO: run minimax on all available moves, return the best one
#         pass
#
#     def _minimax(self, board: Board, is_maximizing: bool, depth: int) -> int:
#         # TODO: recursive minimax
#         pass
