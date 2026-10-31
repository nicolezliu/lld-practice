"""
Core Tic-Tac-Toe game logic.

Your job: implement the TicTacToeGame class.
This is the main entry point — it orchestrates the board, players, and game state.

Think about:
- How do you track whose turn it is?
- How do you detect a win vs a draw?
- What should happen if someone tries to move after the game is over?
"""

from models import Board, Player, Piece, GameState, Move


class TicTacToeGame:
    """
    The main game controller.

    Manages the board, two players, turn order, and win/draw detection.
    """

    def __init__(self, player1: Player, player2: Player):
        """
        Initialize a new game.

        Args:
            player1: the player using Piece.X (goes first)
            player2: the player using Piece.O

        Raise ValueError if both players have the same piece,
        or if neither player has X (X must go first).
        """
        # TODO: validate players, create board, set initial state
        # - Ensure player1 has X and player2 has O (or vice versa)
        # - X always goes first
        # - Initial game state is PLAYING
        pass

    @property
    def current_player(self) -> Player:
        """Return the player whose turn it is."""
        # TODO
        pass

    @property
    def state(self) -> GameState:
        """Return the current game state."""
        # TODO
        pass

    @property
    def board(self) -> Board:
        """Return the game board."""
        # TODO
        pass

    def make_move(self, row: int, col: int) -> GameState:
        """
        Place the current player's piece at (row, col).

        Returns:
            The game state after the move.

        Raises:
            ValueError: if the game is already over.
            ValueError: if the cell is out of bounds or occupied
                        (delegated to Board.place_piece).
        """
        # TODO:
        # 1. Check the game isn't over
        # 2. Place the piece on the board
        # 3. Check for a winner
        # 4. Check for a draw (board full, no winner)
        # 5. Switch turns
        # 6. Return the updated game state
        pass

    def check_winner(self) -> Piece | None:
        """
        Check if there is a winner on the current board.

        Returns:
            Piece.X or Piece.O if that player has won, None otherwise.

        Check:
        - All rows
        - All columns
        - Both diagonals
        """
        # TODO
        pass

    def _switch_turn(self) -> None:
        """Switch the current player to the other player."""
        # TODO
        pass

    def get_available_moves(self) -> list[tuple[int, int]]:
        """Return all valid (row, col) positions where a piece can be placed."""
        # TODO
        pass

    def reset(self) -> None:
        """Reset the game to initial state for a new round."""
        # TODO: clear board, reset state, X goes first again
        pass
