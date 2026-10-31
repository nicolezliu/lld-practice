"""
Test driver for the Tic-Tac-Toe game.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import Player, Piece, GameState
from game import TicTacToeGame
from player_strategy import RandomStrategy


def main():
    print("=" * 60)
    print("TIC-TAC-TOE — LLD PRACTICE")
    print("=" * 60)

    # --- Scenario 1: Human vs Human (scripted moves) ---
    print("\n--- Scenario 1: Scripted game — X wins ---")
    p1 = Player("Alice", Piece.X)
    p2 = Player("Bob", Piece.O)
    game = TicTacToeGame(p1, p2)

    scripted_moves = [
        (0, 0),  # X
        (1, 0),  # O
        (0, 1),  # X
        (1, 1),  # O
        (0, 2),  # X wins — top row
    ]

    for row, col in scripted_moves:
        player = game.current_player
        result = game.make_move(row, col)
        print(f"  {player.name} ({player.piece.value}) plays ({row}, {col})")
        print(game.board)
        print()
        if result != GameState.PLAYING:
            print(f"  >>> Game over: {result.value}")
            break

    # --- Scenario 2: Scripted draw ---
    print("\n--- Scenario 2: Scripted game — Draw ---")
    game = TicTacToeGame(Player("X-Player", Piece.X), Player("O-Player", Piece.O))

    # Known draw sequence:
    #   X O X
    #   X X O
    #   O X O
    draw_moves = [
        (0, 0), (0, 1), (0, 2),
        (1, 2), (1, 1), (2, 0),
        (1, 0), (2, 2), (2, 1),
    ]

    for row, col in draw_moves:
        player = game.current_player
        result = game.make_move(row, col)
        print(f"  {player.name} ({player.piece.value}) plays ({row}, {col})")

    print(game.board)
    print(f"  >>> Game over: {result.value}")

    # --- Scenario 3: Random vs Random ---
    print("\n--- Scenario 3: Random vs Random (single game) ---")
    p1 = Player("Random-X", Piece.X)
    p2 = Player("Random-O", Piece.O)
    game = TicTacToeGame(p1, p2)
    strategy = RandomStrategy()

    move_num = 0
    while game.state == GameState.PLAYING:
        move_num += 1
        player = game.current_player
        row, col = strategy.get_move(game.board)
        result = game.make_move(row, col)
        print(f"  Move {move_num}: {player.name} ({player.piece.value}) -> ({row}, {col})")

    print()
    print(game.board)
    print(f"  >>> Game over: {result.value}")

    # --- Scenario 4: Random vs Random — 100 games ---
    print("\n--- Scenario 4: Random vs Random — 100 games ---")
    results = {GameState.X_WON: 0, GameState.O_WON: 0, GameState.DRAW: 0}

    for _ in range(100):
        game = TicTacToeGame(Player("X", Piece.X), Player("O", Piece.O))
        while game.state == GameState.PLAYING:
            row, col = strategy.get_move(game.board)
            game.make_move(row, col)
        results[game.state] += 1

    print(f"  X wins: {results[GameState.X_WON]}")
    print(f"  O wins: {results[GameState.O_WON]}")
    print(f"  Draws:  {results[GameState.DRAW]}")
    print(f"  Total:  {sum(results.values())}")

    # --- Scenario 5: Error handling ---
    print("\n--- Scenario 5: Error handling ---")
    game = TicTacToeGame(Player("X", Piece.X), Player("O", Piece.O))
    game.make_move(0, 0)

    # Try to play on an occupied cell
    try:
        game.make_move(0, 0)
        print("  ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"  Occupied cell caught: {e}")

    # Try out-of-bounds move
    try:
        game.make_move(5, 5)
        print("  ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"  Out of bounds caught: {e}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens if you play after the game is over?
    #   - Try resetting the game and playing again
    #   - Implement MinimaxStrategy and see if it ever loses


if __name__ == "__main__":
    main()
