"""
Phased tests for the Tic-Tac-Toe game.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Game logic only
    python -m pytest tests.py -v -k "phase3"    # Strategy + full simulation

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest

from models import Piece, GameState, Move, Player, Board
from game import TicTacToeGame
from player_strategy import RandomStrategy


# ===================================================================
# PHASE 1: Models — Enums, Move, Player, Board
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_piece_members(self):
        assert Piece.X
        assert Piece.O
        assert Piece.EMPTY

    def test_game_state_members(self):
        assert GameState.PLAYING
        assert GameState.X_WON
        assert GameState.O_WON
        assert GameState.DRAW


class TestPhase1Move:
    """Verify Move dataclass."""

    def test_move_fields(self):
        m = Move(row=1, col=2, piece=Piece.X)
        assert m.row == 1
        assert m.col == 2
        assert m.piece == Piece.X

    def test_move_equality(self):
        m1 = Move(0, 0, Piece.X)
        m2 = Move(0, 0, Piece.X)
        assert m1 == m2

    def test_move_inequality(self):
        m1 = Move(0, 0, Piece.X)
        m2 = Move(0, 1, Piece.X)
        assert m1 != m2


class TestPhase1Player:
    """Verify Player creation."""

    def test_player_name(self):
        p = Player("Alice", Piece.X)
        assert p.name == "Alice"

    def test_player_piece(self):
        p = Player("Bob", Piece.O)
        assert p.piece == Piece.O

    def test_player_repr(self):
        p = Player("Alice", Piece.X)
        assert "Alice" in repr(p)


class TestPhase1Board:
    """Verify Board state management."""

    def test_new_board_is_empty(self):
        b = Board()
        for r in range(3):
            for c in range(3):
                assert b.get_piece(r, c) == Piece.EMPTY

    def test_board_size(self):
        b = Board()
        assert b.size == 3

    def test_custom_board_size(self):
        b = Board(size=5)
        assert b.size == 5

    def test_place_piece(self):
        b = Board()
        b.place_piece(0, 0, Piece.X)
        assert b.get_piece(0, 0) == Piece.X

    def test_place_piece_out_of_bounds_raises(self):
        b = Board()
        with pytest.raises(ValueError):
            b.place_piece(3, 0, Piece.X)
        with pytest.raises(ValueError):
            b.place_piece(0, -1, Piece.X)

    def test_place_piece_occupied_raises(self):
        b = Board()
        b.place_piece(1, 1, Piece.X)
        with pytest.raises(ValueError):
            b.place_piece(1, 1, Piece.O)

    def test_place_empty_piece_raises(self):
        b = Board()
        with pytest.raises(ValueError):
            b.place_piece(0, 0, Piece.EMPTY)

    def test_get_piece_out_of_bounds_raises(self):
        b = Board()
        with pytest.raises(ValueError):
            b.get_piece(5, 0)

    def test_is_full_empty_board(self):
        b = Board()
        assert b.is_full() is False

    def test_is_full_full_board(self):
        b = Board()
        pieces = [Piece.X, Piece.O]
        idx = 0
        for r in range(3):
            for c in range(3):
                b.place_piece(r, c, pieces[idx % 2])
                idx += 1
        assert b.is_full() is True

    def test_get_empty_cells(self):
        b = Board()
        assert len(b.get_empty_cells()) == 9
        b.place_piece(0, 0, Piece.X)
        assert len(b.get_empty_cells()) == 8
        assert (0, 0) not in b.get_empty_cells()

    def test_reset_clears_board(self):
        b = Board()
        b.place_piece(0, 0, Piece.X)
        b.place_piece(1, 1, Piece.O)
        b.reset()
        assert b.get_piece(0, 0) == Piece.EMPTY
        assert b.get_piece(1, 1) == Piece.EMPTY
        assert len(b.get_empty_cells()) == 9

    def test_board_str_not_empty(self):
        b = Board()
        b.place_piece(0, 0, Piece.X)
        s = str(b)
        assert "X" in s


# ===================================================================
# PHASE 2: Game Logic — make_move, check_winner, draw
# ===================================================================

class TestPhase2GameSetup:
    """Verify game initialization and player validation."""

    def test_game_creation(self):
        p1 = Player("Alice", Piece.X)
        p2 = Player("Bob", Piece.O)
        game = TicTacToeGame(p1, p2)
        assert game.state == GameState.PLAYING

    def test_x_goes_first(self):
        p1 = Player("Alice", Piece.X)
        p2 = Player("Bob", Piece.O)
        game = TicTacToeGame(p1, p2)
        assert game.current_player.piece == Piece.X

    def test_x_goes_first_reversed_order(self):
        """Even if O is passed first, X should still go first."""
        p1 = Player("Alice", Piece.O)
        p2 = Player("Bob", Piece.X)
        game = TicTacToeGame(p1, p2)
        assert game.current_player.piece == Piece.X

    def test_same_piece_raises(self):
        p1 = Player("Alice", Piece.X)
        p2 = Player("Bob", Piece.X)
        with pytest.raises(ValueError):
            TicTacToeGame(p1, p2)


class TestPhase2MakeMove:
    """Verify move placement and turn switching."""

    def _make_game(self) -> TicTacToeGame:
        return TicTacToeGame(Player("X", Piece.X), Player("O", Piece.O))

    def test_first_move_places_x(self):
        game = self._make_game()
        game.make_move(0, 0)
        assert game.board.get_piece(0, 0) == Piece.X

    def test_turns_alternate(self):
        game = self._make_game()
        game.make_move(0, 0)  # X
        assert game.current_player.piece == Piece.O
        game.make_move(1, 1)  # O
        assert game.current_player.piece == Piece.X

    def test_invalid_move_out_of_bounds(self):
        game = self._make_game()
        with pytest.raises(ValueError):
            game.make_move(3, 0)

    def test_invalid_move_occupied(self):
        game = self._make_game()
        game.make_move(0, 0)
        with pytest.raises(ValueError):
            game.make_move(0, 0)


class TestPhase2WinDetection:
    """Verify win detection for rows, columns, and diagonals."""

    def _make_game(self) -> TicTacToeGame:
        return TicTacToeGame(Player("X", Piece.X), Player("O", Piece.O))

    def test_x_wins_row(self):
        game = self._make_game()
        game.make_move(0, 0)  # X
        game.make_move(1, 0)  # O
        game.make_move(0, 1)  # X
        game.make_move(1, 1)  # O
        result = game.make_move(0, 2)  # X wins row 0
        assert result == GameState.X_WON

    def test_o_wins_column(self):
        game = self._make_game()
        game.make_move(0, 0)  # X
        game.make_move(0, 1)  # O
        game.make_move(1, 0)  # X
        game.make_move(1, 1)  # O
        game.make_move(2, 2)  # X
        result = game.make_move(2, 1)  # O wins column 1
        assert result == GameState.O_WON

    def test_x_wins_main_diagonal(self):
        game = self._make_game()
        game.make_move(0, 0)  # X
        game.make_move(0, 1)  # O
        game.make_move(1, 1)  # X
        game.make_move(0, 2)  # O
        result = game.make_move(2, 2)  # X wins diagonal
        assert result == GameState.X_WON

    def test_o_wins_anti_diagonal(self):
        game = self._make_game()
        game.make_move(1, 0)  # X
        game.make_move(0, 2)  # O
        game.make_move(2, 2)  # X
        game.make_move(1, 1)  # O
        game.make_move(0, 0)  # X
        result = game.make_move(2, 0)  # O wins anti-diagonal
        assert result == GameState.O_WON

    def test_no_winner_yet(self):
        game = self._make_game()
        result = game.make_move(0, 0)  # X
        assert result == GameState.PLAYING


class TestPhase2Draw:
    """Verify draw detection."""

    def _make_game(self) -> TicTacToeGame:
        return TicTacToeGame(Player("X", Piece.X), Player("O", Piece.O))

    def test_draw_full_board(self):
        """
        Board state for a draw:
          X | O | X
          X | X | O
          O | X | O
        """
        game = self._make_game()
        moves = [
            (0, 0),  # X
            (0, 1),  # O
            (0, 2),  # X
            (1, 0),  # O — wait, need to ensure draw
        ]
        # A known draw sequence:
        #   X O X
        #   X X O
        #   O X O
        # Moves: X(0,0) O(0,1) X(0,2) O(1,2) X(1,1) O(2,0) X(1,0) O(2,2) X(2,1)
        draw_moves = [
            (0, 0), (0, 1), (0, 2),  # X, O, X
            (1, 2), (1, 1), (2, 0),  # O, X, O
            (1, 0), (2, 2), (2, 1),  # X, O, X
        ]
        for r, c in draw_moves[:-1]:
            result = game.make_move(r, c)
            assert result == GameState.PLAYING
        result = game.make_move(*draw_moves[-1])
        assert result == GameState.DRAW

    def test_move_after_game_over_raises(self):
        game = self._make_game()
        # X wins row 0
        game.make_move(0, 0)  # X
        game.make_move(1, 0)  # O
        game.make_move(0, 1)  # X
        game.make_move(1, 1)  # O
        game.make_move(0, 2)  # X wins
        with pytest.raises(ValueError):
            game.make_move(2, 2)

    def test_available_moves_decrease(self):
        game = self._make_game()
        assert len(game.get_available_moves()) == 9
        game.make_move(0, 0)
        assert len(game.get_available_moves()) == 8

    def test_reset_restores_game(self):
        game = self._make_game()
        game.make_move(0, 0)
        game.make_move(1, 1)
        game.reset()
        assert game.state == GameState.PLAYING
        assert game.current_player.piece == Piece.X
        assert len(game.get_available_moves()) == 9


# ===================================================================
# PHASE 3: Strategy + Full Game Simulation
# ===================================================================

class TestPhase3RandomStrategy:
    """Verify the RandomStrategy picks valid moves."""

    def test_returns_empty_cell(self):
        b = Board()
        b.place_piece(0, 0, Piece.X)
        strategy = RandomStrategy()
        row, col = strategy.get_move(b)
        assert b.get_piece(row, col) == Piece.EMPTY

    def test_returns_last_empty_cell(self):
        b = Board()
        # Fill all but (2, 2)
        pieces = [Piece.X, Piece.O]
        idx = 0
        for r in range(3):
            for c in range(3):
                if (r, c) != (2, 2):
                    b.place_piece(r, c, pieces[idx % 2])
                    idx += 1
        strategy = RandomStrategy()
        row, col = strategy.get_move(b)
        assert (row, col) == (2, 2)

    def test_different_moves_over_multiple_calls(self):
        """Over many calls on an empty board, we should see different moves."""
        b = Board()
        strategy = RandomStrategy()
        moves = set()
        for _ in range(50):
            move = strategy.get_move(b)
            moves.add(move)
        # With 9 possible cells and 50 attempts, we should see at least 2 different moves
        assert len(moves) >= 2


class TestPhase3FullSimulation:
    """Verify a complete game can be played with strategies."""

    def test_random_vs_random_completes(self):
        """Two random players should always finish a game."""
        p1 = Player("Random-X", Piece.X)
        p2 = Player("Random-O", Piece.O)
        game = TicTacToeGame(p1, p2)
        strategy = RandomStrategy()

        while game.state == GameState.PLAYING:
            row, col = strategy.get_move(game.board)
            game.make_move(row, col)

        assert game.state in (GameState.X_WON, GameState.O_WON, GameState.DRAW)

    def test_random_vs_random_ten_games(self):
        """Run 10 random games — all should complete without errors."""
        results = {GameState.X_WON: 0, GameState.O_WON: 0, GameState.DRAW: 0}
        for _ in range(10):
            p1 = Player("X", Piece.X)
            p2 = Player("O", Piece.O)
            game = TicTacToeGame(p1, p2)
            strategy = RandomStrategy()
            while game.state == GameState.PLAYING:
                row, col = strategy.get_move(game.board)
                game.make_move(row, col)
            results[game.state] += 1

        assert sum(results.values()) == 10

    def test_game_reset_allows_replay(self):
        """After reset, a full new game should work."""
        p1 = Player("X", Piece.X)
        p2 = Player("O", Piece.O)
        game = TicTacToeGame(p1, p2)
        strategy = RandomStrategy()

        # Play first game
        while game.state == GameState.PLAYING:
            row, col = strategy.get_move(game.board)
            game.make_move(row, col)
        first_result = game.state

        # Reset and play again
        game.reset()
        assert game.state == GameState.PLAYING
        while game.state == GameState.PLAYING:
            row, col = strategy.get_move(game.board)
            game.make_move(row, col)
        second_result = game.state

        assert first_result in (GameState.X_WON, GameState.O_WON, GameState.DRAW)
        assert second_result in (GameState.X_WON, GameState.O_WON, GameState.DRAW)

    def test_x_always_moves_first_after_reset(self):
        p1 = Player("X", Piece.X)
        p2 = Player("O", Piece.O)
        game = TicTacToeGame(p1, p2)

        game.make_move(0, 0)  # X
        game.make_move(1, 1)  # O
        game.reset()
        assert game.current_player.piece == Piece.X

    def test_board_tracks_all_moves(self):
        """Every move should be reflected on the board."""
        p1 = Player("X", Piece.X)
        p2 = Player("O", Piece.O)
        game = TicTacToeGame(p1, p2)

        game.make_move(0, 0)  # X
        game.make_move(1, 1)  # O
        game.make_move(2, 2)  # X

        assert game.board.get_piece(0, 0) == Piece.X
        assert game.board.get_piece(1, 1) == Piece.O
        assert game.board.get_piece(2, 2) == Piece.X
