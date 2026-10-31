"""
SOLUTION — Tic-Tac-Toe Game

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

This solution uses:
- Enum-based state tracking for pieces and game state
- Strategy pattern for move selection (random AI)
- Dataclass for moves
- Step-based game loop with explicit turn management
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
import random


# ===================================================================
# Enums
# ===================================================================

class Piece(Enum):
    X = "X"
    O = "O"
    EMPTY = "."


class GameState(Enum):
    PLAYING = "PLAYING"
    X_WON = "X_WON"
    O_WON = "O_WON"
    DRAW = "DRAW"


# ===================================================================
# Move
# ===================================================================

@dataclass
class Move:
    row: int
    col: int
    piece: Piece


# ===================================================================
# Player
# ===================================================================

class Player:
    def __init__(self, name: str, piece: Piece):
        self._name = name
        self._piece = piece

    @property
    def name(self) -> str:
        return self._name

    @property
    def piece(self) -> Piece:
        return self._piece

    def __repr__(self) -> str:
        return f"Player({self._name}, {self._piece.value})"


# ===================================================================
# Board
# ===================================================================

class Board:
    """
    Key design decisions:

    1. The grid is a list of lists — simple and direct. Each cell
       holds a Piece enum value (X, O, or EMPTY).

    2. Bounds checking is done in place_piece and get_piece rather
       than silently returning defaults. Fail-fast is better for a
       game where invalid moves should never happen silently.

    3. The size parameter allows stretch-goal NxN boards without
       changing any logic.
    """

    def __init__(self, size: int = 3):
        self._size = size
        self._grid: list[list[Piece]] = [
            [Piece.EMPTY for _ in range(size)] for _ in range(size)
        ]

    @property
    def size(self) -> int:
        return self._size

    def _validate_coords(self, row: int, col: int) -> None:
        if row < 0 or row >= self._size or col < 0 or col >= self._size:
            raise ValueError(
                f"Coordinates ({row}, {col}) out of bounds for "
                f"{self._size}x{self._size} board"
            )

    def place_piece(self, row: int, col: int, piece: Piece) -> None:
        self._validate_coords(row, col)
        if piece == Piece.EMPTY:
            raise ValueError("Cannot place an EMPTY piece")
        if self._grid[row][col] != Piece.EMPTY:
            raise ValueError(
                f"Cell ({row}, {col}) is already occupied by "
                f"{self._grid[row][col].value}"
            )
        self._grid[row][col] = piece

    def get_piece(self, row: int, col: int) -> Piece:
        self._validate_coords(row, col)
        return self._grid[row][col]

    def is_full(self) -> bool:
        return all(
            self._grid[r][c] != Piece.EMPTY
            for r in range(self._size)
            for c in range(self._size)
        )

    def reset(self) -> None:
        self._grid = [
            [Piece.EMPTY for _ in range(self._size)] for _ in range(self._size)
        ]

    def get_empty_cells(self) -> list[tuple[int, int]]:
        return [
            (r, c)
            for r in range(self._size)
            for c in range(self._size)
            if self._grid[r][c] == Piece.EMPTY
        ]

    def __str__(self) -> str:
        rows = []
        for r in range(self._size):
            cells = [self._grid[r][c].value for c in range(self._size)]
            rows.append(" | ".join(cells))
        separator = "\n" + "-" * (self._size * 4 - 3) + "\n"
        return separator.join(rows)


# ===================================================================
# TicTacToeGame (the orchestrator)
# ===================================================================

class TicTacToeGame:
    """
    Key design decisions:

    1. The game enforces X-goes-first regardless of the order players
       are passed to the constructor. This keeps the rules consistent.

    2. Win detection checks all rows, columns, and both diagonals
       after every move. For a 3x3 board this is trivially fast.
       For NxN boards you'd want incremental checking.

    3. The game state is updated immediately after each move —
       there's no separate "evaluate" step. This prevents the board
       from being in an inconsistent state.

    4. Moves after game-over raise ValueError rather than silently
       failing. Fail-fast prevents bugs in game loop logic.
    """

    def __init__(self, player1: Player, player2: Player):
        if player1.piece == player2.piece:
            raise ValueError("Players must have different pieces")

        # Ensure we know who is X and who is O
        if player1.piece == Piece.X:
            self._player_x = player1
            self._player_o = player2
        elif player2.piece == Piece.X:
            self._player_x = player2
            self._player_o = player1
        else:
            raise ValueError("One player must use Piece.X")

        self._board = Board()
        self._state = GameState.PLAYING
        self._current_player = self._player_x  # X always goes first

    @property
    def current_player(self) -> Player:
        return self._current_player

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def board(self) -> Board:
        return self._board

    def make_move(self, row: int, col: int) -> GameState:
        if self._state != GameState.PLAYING:
            raise ValueError(
                f"Game is already over with state {self._state.value}"
            )

        # Place the piece (Board validates coordinates and occupancy)
        self._board.place_piece(row, col, self._current_player.piece)

        # Check for winner
        winner = self.check_winner()
        if winner == Piece.X:
            self._state = GameState.X_WON
            return self._state
        elif winner == Piece.O:
            self._state = GameState.O_WON
            return self._state

        # Check for draw
        if self._board.is_full():
            self._state = GameState.DRAW
            return self._state

        # Switch turns
        self._switch_turn()
        return self._state

    def check_winner(self) -> Piece | None:
        size = self._board.size

        # Check rows
        for r in range(size):
            first = self._board.get_piece(r, 0)
            if first != Piece.EMPTY and all(
                self._board.get_piece(r, c) == first for c in range(size)
            ):
                return first

        # Check columns
        for c in range(size):
            first = self._board.get_piece(0, c)
            if first != Piece.EMPTY and all(
                self._board.get_piece(r, c) == first for r in range(size)
            ):
                return first

        # Check main diagonal (top-left to bottom-right)
        first = self._board.get_piece(0, 0)
        if first != Piece.EMPTY and all(
            self._board.get_piece(i, i) == first for i in range(size)
        ):
            return first

        # Check anti-diagonal (top-right to bottom-left)
        first = self._board.get_piece(0, size - 1)
        if first != Piece.EMPTY and all(
            self._board.get_piece(i, size - 1 - i) == first for i in range(size)
        ):
            return first

        return None

    def _switch_turn(self) -> None:
        if self._current_player is self._player_x:
            self._current_player = self._player_o
        else:
            self._current_player = self._player_x

    def get_available_moves(self) -> list[tuple[int, int]]:
        return self._board.get_empty_cells()

    def reset(self) -> None:
        self._board.reset()
        self._state = GameState.PLAYING
        self._current_player = self._player_x


# ===================================================================
# Move strategies (Strategy pattern)
# ===================================================================

class MoveStrategy(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> tuple[int, int]:
        ...


class RandomStrategy(MoveStrategy):
    """
    Picks a random empty cell. Simple but useful as a baseline
    and for testing that the game loop works end-to-end.
    """

    def get_move(self, board: Board) -> tuple[int, int]:
        empty = board.get_empty_cells()
        if not empty:
            raise ValueError("No available moves on the board")
        return random.choice(empty)
