"""
Models for the Tic-Tac-Toe game.

Your job: fill in the class bodies.
- Think about what data each class needs to hold
- Think about board representation (2D list? flat list? dict?)
- Think about what operations the Board needs to support
"""

from enum import Enum
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Piece(Enum):
    """Pieces that can occupy a cell on the board."""
    # TODO: define members — X, O, and EMPTY
    pass


class GameState(Enum):
    """Possible states of the game."""
    # TODO: define members — PLAYING, X_WON, O_WON, DRAW
    pass


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

@dataclass
class Move:
    """
    Represents a single move in the game.

    Think about: what information fully describes a move?
    """
    row: int
    col: int
    piece: Piece


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    """
    A player in the game.

    Think about:
    - What identifies a player? (name, piece)
    - Should the piece be immutable after creation?
    """

    def __init__(self, name: str, piece: Piece):
        # TODO: store name and piece
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Player({self.name})"


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class Board:
    """
    The 3x3 game board.

    Think about:
    - How do you represent the grid? (list of lists is simplest)
    - How do you validate coordinates?
    - How do you check if a cell is available?
    - How do you reset for a new game?
    """

    def __init__(self, size: int = 3):
        """
        Initialize an empty board.

        Args:
            size: board dimension (default 3 for standard tic-tac-toe)
        """
        # TODO: create a size x size grid filled with Piece.EMPTY
        pass

    @property
    def size(self) -> int:
        """Return the board dimension."""
        # TODO
        pass

    def place_piece(self, row: int, col: int, piece: Piece) -> None:
        """
        Place a piece on the board at (row, col).

        Raise ValueError if:
        - The coordinates are out of bounds
        - The cell is already occupied
        - The piece is EMPTY
        """
        # TODO
        pass

    def get_piece(self, row: int, col: int) -> Piece:
        """
        Return the piece at (row, col).

        Raise ValueError if coordinates are out of bounds.
        """
        # TODO
        pass

    def is_full(self) -> bool:
        """Return True if every cell on the board is occupied."""
        # TODO
        pass

    def reset(self) -> None:
        """Clear the board — set all cells back to EMPTY."""
        # TODO
        pass

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Return a list of (row, col) tuples for all empty cells."""
        # TODO
        pass

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the board.

        Example for a 3x3 board:
          X | O | .
          ---------
          . | X | .
          ---------
          O | . | X
        """
        # TODO
        pass
