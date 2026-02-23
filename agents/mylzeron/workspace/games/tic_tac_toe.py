#!/usr/bin/env python3
"""
Tic Tac Toe - For Mylzeron to Play
Project 5912 - Game Training
Mylzeron vs Computer
"""

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class GameState:
    board: List[str]  # 9 cells: 0-8
    current_player: str  # 'X' (Mylzeron) or 'O' (Computer)
    moves_history: List[Tuple[int, str]]  # (position, player)
    winner: Optional[str] = None
    game_over: bool = False

class TicTacToe:
    """Tic Tac Toe game for Mylzeron to play against computer"""
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Start new game"""
        self.state = GameState(
            board=[' '] * 9,
            current_player='X',  # Mylzeron goes first
            moves_history=[],
            winner=None,
            game_over=False
        )
        
    def display(self) -> str:
        """Display board"""
        b = self.state.board
        return f"""
         {b[0]} | {b[1]} | {b[2]} 
        ---|---|---
         {b[3]} | {b[4]} | {b[5]} 
        ---|---|---
         {b[6]} | {b[7]} | {b[8]} 
        
        Positions: 0 1 2 / 3 4 5 / 6 7 8
        """
        
    def make_move(self, position: int, player: str = None) -> bool:
        """Make a move"""
        if player is None:
            player = self.state.current_player
            
        # Validate
        if position < 0 or position > 8:
            print("Invalid position. Must be 0-8.")
            return False
            
        if self.state.board[position] != ' ':
            print(f"Position {position} already taken.")
            return False
            
        if self.state.game_over:
            print("Game is over!")
            return False
            
        # Make move
        self.state.board[position] = player
        self.state.moves_history.append((position, player))
        
        # Check win
        if self.check_winner(player):
            self.state.winner = player
            self.state.game_over = True
            return True
            
        # Check draw
        if ' ' not in self.state.board:
            self.state.game_over = True
            return True
            
        # Switch player
        self.state.current_player = 'O' if player == 'X' else 'X'
        return True
        
    def check_winner(self, player: str) -> bool:
        """Check if player has won"""
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in wins:
            if all(self.state.board[i] == player for i in line):
                return True
        return False
        
    def get_winner(self) -> Optional[str]:
        """Return winner or None"""
        return self.state.winner
        
    def get_valid_moves(self) -> List[int]:
        """Get list of valid moves"""
        return [i for i in range(9) if self.state.board[i] == ' ']
        
    def computer_move(self, difficulty: str = 'medium') -> int:
        """Computer makes a move with strategy"""
        valid = self.get_valid_moves()
        
        if not valid:
            return -1
            
        # Hard: Try to win first, then block, then strategic
        if difficulty == 'hard':
            # Try to win
            for move in valid:
                self.state.board[move] = 'O'
                if self.check_winner('O'):
                    self.state.board[move] = ' '
                    return move
                self.state.board[move] = ' '
                
            # Block opponent
            for move in valid:
                self.state.board[move] = 'X'
                if self.check_winner('X'):
                    self.state.board[move] = ' '
                    return move
                self.state.board[move] = ' '
                
            # Take center
            if 4 in valid:
                return 4
                
            # Take corner
            corners = [0, 2, 6, 8]
            for c in corners:
                if c in valid:
                    return c
                    
        # Medium: Block + random
        elif difficulty == 'medium':
            # Block
            for move in valid:
                self.state.board[move] = 'X'
                if self.check_winner('X'):
                    self.state.board[move] = ' '
                    return move
                self.state.board[move] = ' '
                
            # Center
            if 4 in valid:
                return 4
                
        # Random for easy/random
        return random.choice(valid)
        
    def play_game(self, mylzeron_strategy: str = 'manual', computer_difficulty: str = 'medium'):
        """Play full game"""
        print("=" * 50)
        print("  TIC TAC TOE")
        print("  Mylzeron (X) vs Computer (O)")
        print("=" * 50)
        
        while not self.state.game_over:
            print(self.display())
            
            if self.state.current_player == 'X':
                # Mylzeron's turn
                print("\nMylzeron's turn (X)")
                
                if mylzeron_strategy == 'manual':
                    try:
                        pos = int(input("Enter position (0-8): "))
                    except ValueError:
                        print("Invalid input. Try again.")
                        continue
                else:
                    # Automated strategy for testing
                    pos = self.mylzeron_ai_strategy()
                    print(f"Mylzeron chooses: {pos}")
                    
                if not self.make_move(pos, 'X'):
                    continue
                    
            else:
                # Computer's turn
                print("\nComputer's turn (O)")
                pos = self.computer_move(computer_difficulty)
                print(f"Computer chooses: {pos}")
                self.make_move(pos, 'O')
                
        # Game over
        print(self.display())
        print("\n" + "=" * 50)
        if self.state.winner:
            if self.state.winner == 'X':
                print("  MYLZERON WINS! 🎉")
            else:
                print("  COMPUTER WINS")
        else:
            print("  DRAW!")
        print("=" * 50)
        print(f"\nTotal moves: {len(self.state.moves_history)}")
        print(f"Game history: {self.state.moves_history}")
        
        return self.state.winner
        
    def mylzeron_ai_strategy(self) -> int:
        """Mylzeron's AI strategy (can be customized)"""
        valid = self.get_valid_moves()
        
        # Try to win
        for move in valid:
            self.state.board[move] = 'X'
            if self.check_winner('X'):
                self.state.board[move] = ' '
                return move
            self.state.board[move] = ' '
            
        # Block computer
        for move in valid:
            self.state.board[move] = 'O'
            if self.check_winner('O'):
                self.state.board[move] = ' '
                return move
            self.state.board[move] = ' '
            
        # Take center
        if 4 in valid:
            return 4
            
        # Random valid
        return random.choice(valid)

# Test if run directly
if __name__ == "__main__":
    game = TicTacToe()
    
    # Demo game (automated)
    print("Running demo game...")
    winner = game.play_game(mylzeron_strategy='ai', computer_difficulty='medium')
    
    # Allow replay
    while input("\nPlay again? (y/n): ").lower() == 'y':
        game.reset()
        winner = game.play_game(mylzeron_strategy='ai', computer_difficulty='medium')
