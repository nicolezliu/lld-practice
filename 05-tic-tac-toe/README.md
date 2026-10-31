# Tic-Tac-Toe Game — LLD Practice

## Problem Statement
Design a Tic-Tac-Toe game for 2 players on a 3x3 board.

## Requirements

### Functional
- The board is a 3x3 grid, each cell is either X, O, or empty
- Two players take turns placing their piece (X or O) on the board
- X always goes first
- A player wins by placing three of their pieces in a row (horizontal, vertical, or diagonal)
- The game is a draw if the board is full and no player has won
- The system tracks the current game state: PLAYING, X_WON, O_WON, or DRAW
- Invalid moves (out of bounds, occupied cell, move after game over) are rejected

### Non-Functional
- Extensible to different player strategies (human, random AI, minimax AI)
- Clean separation between game logic, board state, and player strategy

## Suggested Design Patterns
- **Strategy** — for player move selection (human input vs AI algorithms)
- **Observer** — for game events (move made, game won, game drawn)
- **State** — for game states (PLAYING, X_WON, O_WON, DRAW)

## Your Task
1. Fill in the class bodies in `models.py` (enums, Board, Player, Move)
2. Implement the game logic in `game.py` (TicTacToeGame)
3. Implement move strategies in `player_strategy.py` (RandomStrategy)
4. Run `main.py` to test your design end-to-end
5. Try swapping strategies and see how behavior changes

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, Board, Player, Move
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Game logic — make_move, check_winner, draw detection
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: Strategy + full game simulation
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Support NxN boards with configurable win length
- Implement a MinimaxStrategy that plays optimally (never loses)
- Add an undo/redo feature for moves
- Add an Observer that logs every game event
