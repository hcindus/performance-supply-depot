#!/usr/bin/env python3
"""
Checkers - For Mylzeron to Play
Project 5912 - Game Training
Mylzeron vs Computer
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

@dataclass
class Piece:
    player: str  # 'R' (Mylzeron - Red) or 'B' (Computer - Black)
    king: bool = False
    
    def __str__(self):
        return 'RK' if self.player == 'R' and self.king else 'BK' if self.player == 'B' and self.king else self.player

@dataclass
class GameState:
    board: List[List[Optional[Piece]]]  # 8x8 grid
    current_player: str  # 'R' (Mylzeron) or 'B' (Computer)
    move_history: List[Dict] = field(default_factory=list)
    red_pieces: int = 12
    black_pieces: int = 12
    winner: Optional[str] = None
    game_over: bool = False
    turns_without_capture: int = 0  # For stalemate detection

class Checkers:
    """Checkers game for Mylzeron to play"""
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Initialize board"""
        board = [[None] * 8 for _ in range(8)]
        
        # Black pieces (top, rows 0-2)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece('B')
                    
        # Red pieces (bottom, rows 5-7)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece('R')
                    
        self.state = GameState(
            board=board,
            current_player='R',  # Mylzeron goes first (Red)
            move_history=[],
            red_pieces=12,
            black_pieces=12,
            winner=None,
            game_over=False,
            turns_without_capture=0
        )
        
    def display(self) -> str:
        """Display board"""
        result = "\n    0   1   2   3   4   5   6   7\n"
        result += "  +---+---+---+---+---+---+---+---+\n"
        
        for row in range(8):
            result += f"{row} |"
            for col in range(8):
                piece = self.state.board[row][col]
                if piece:
                    result += f" {piece} |"
                else:
                    result += "   |"
            result += f"\n  +---+---+---+---+---+---+---+---+\n"
            
        result += f"\n  Mylzeron (Red): {self.state.red_pieces} pieces"
        result += f"\n  Computer (Black): {self.state.black_pieces} pieces\n"
        return result
        
    def get_valid_moves(self, player: str = None) -> List[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """Get all valid moves for player"""
        if player is None:
            player = self.state.current_player
            
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.state.board[row][col]
                if piece and piece.player == player:
                    piece_moves = self.get_piece_moves(row, col)
                    if piece_moves:
                        moves.append(((row, col), piece_moves))
                        
        return moves
        
    def get_piece_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid moves for specific piece"""
        piece = self.state.board[row][col]
        if not piece:
            return []
            
        moves = []
        captures = []
        
        # Direction depends on player and king status
        if piece.player == 'R':  # Red moves up (decreasing row)
            directions = [(-1, -1), (-1, 1)]
            if piece.king:
                directions.extend([(1, -1), (1, 1)])
        else:  # Black moves down (increasing row)
            directions = [(1, -1), (1, 1)]
            if piece.king:
                directions.extend([(-1, -1), (-1, 1)])
                
        for dr, dc in directions:
            # Normal move
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if self.state.board[nr][nc] is None:
                    moves.append((nr, nc))
                else:
                    # Capture move
                    if self.state.board[nr][nc].player != piece.player:
                        cr, cc = nr + dr, nc + dc
                        if 0 <= cr < 8 and 0 <= cc < 8:
                            if self.state.board[cr][cc] is None:
                                captures.append((cr, cc))
                                
        # Captures are mandatory
        return captures if captures else moves
        
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], player: str = None) -> bool:
        """Execute a move"""
        if player is None:
            player = self.state.current_player
            
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Validate
        piece = self.state.board[from_row][from_col]
        if not piece:
            print(f"No piece at {from_pos}")
            return False
            
        if piece.player != player:
            print(f"Not your piece")
            return False
            
        valid_moves = self.get_piece_moves(from_row, from_col)
        if to_pos not in valid_moves:
            print(f"Invalid move: {from_pos} -> {to_pos}")
            return False
            
        # Execute move
        self.state.board[to_row][to_col] = piece
        self.state.board[from_row][from_col] = None
        
        # Check for capture
        captured = False
        if abs(to_row - from_row) == 2:
            cap_row = (from_row + to_row) // 2
            cap_col = (from_col + to_col) // 2
            captured_piece = self.state.board[cap_row][cap_col]
            if captured_piece:
                self.state.board[cap_row][cap_col] = None
                captured = True
                
                # Update piece count
                if captured_piece.player == 'R':
                    self.state.red_pieces -= 1
                else:
                    self.state.black_pieces -= 1
                    
                # Check for double jump
                double_jumps = self.get_piece_moves(to_row, to_col)
                double_captures = [m for m in double_jumps if abs(m[0] - to_row) == 2]
                if double_captures:
                    # Must continue capturing
                    pass  # Logic handled elsewhere
                    
        # King promotion
        if player == 'R' and to_row == 0:
            piece.king = True
            print(f"Red piece promoted to King at {to_pos}!")
        elif player == 'B' and to_row == 7:
            piece.king = True
            print(f"Black piece promoted to King at {to_pos}!")
            
        # Update history
        self.state.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'player': player,
            'captured': captured,
            'king_promotion': piece.king and not (from_row == 0 or from_row == 7)
        })
        
        # Update capture tracking
        if captured:
            self.state.turns_without_capture = 0
        else:
            self.state.turns_without_capture += 1
            
        # Check win conditions
        if self.state.red_pieces == 0:
            self.state.winner = 'B'
            self.state.game_over = True
        elif self.state.black_pieces == 0:
            self.state.winner = 'R'
            self.state.game_over = True
        elif self.state.turns_without_capture >= 40:  # Stalemate
            self.state.game_over = True
            self.state.winner = None  # Draw
        elif not self.get_valid_moves('B'):
            self.state.winner = 'R'
            self.state.game_over = True
        elif not self.get_valid_moves('R'):
            self.state.winner = 'B'
            self.state.game_over = True
        else:
            # Switch player if no double jump
            if not captured or not [m for m in self.get_piece_moves(to_row, to_col) 
                                     if abs(m[0] - to_row) == 2]:
                self.state.current_player = 'B' if player == 'R' else 'R'
                
        return True
        
    def computer_move(self, difficulty: str = 'medium') -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Computer makes a move"""
        all_moves = self.get_valid_moves('B')
        
        if not all_moves:
            return ((-1, -1), (-1, -1))
            
        # Flatten moves
        flat_moves = []
        for from_pos, to_list in all_moves:
            for to_pos in to_list:
                flat_moves.append((from_pos, to_pos))
                
        if not flat_moves:
            return ((-1, -1), (-1, -1))
            
        # Find captures (mandatory)
        captures = [m for m in flat_moves if abs(m[1][0] - m[0][0]) == 2]
        
        if captures:
            # Choose best capture
            if difficulty == 'hard':
                # Prioritize captures that lead to king or multiple captures
                return random.choice(captures)
            else:
                return random.choice(captures)
                
        # Regular move
        if difficulty == 'hard':
            # Prioritize moves toward king row or defensive
            king_row_moves = [m for m in flat_moves if m[1][0] == 7]
            if king_row_moves:
                return random.choice(king_row_moves)
                
        return random.choice(flat_moves)
        
    def mylzeron_ai_move(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Mylzeron's strategy"""
        all_moves = self.get_valid_moves('R')
        
        if not all_moves:
            return ((-1, -1), (-1, -1))
            
        flat_moves = []
        for from_pos, to_list in all_moves:
            for to_pos in to_list:
                flat_moves.append((from_pos, to_pos))
                
        # Find captures (mandatory)
        captures = [m for m in flat_moves if abs(m[1][0] - m[0][0]) == 2]
        if captures:
            return random.choice(captures)
            
        # Try to get king
        king_row_moves = [m for m in flat_moves if m[1][0] == 0]
        if king_row_moves:
            return random.choice(king_row_moves)
            
        return random.choice(flat_moves)
        
    def play_game(self, mylzeron_strategy: str = 'manual', computer_difficulty: str = 'medium'):
        """Play full game"""
        print("=" * 50)
        print("  CHECKERS")
        print("  Mylzeron (Red) vs Computer (Black)")
        print("=" * 50)
        
        while not self.state.game_over:
            print(self.display())
            
            if self.state.current_player == 'R':
                print("\nMylzeron's turn (Red)")
                
                if mylzeron_strategy == 'manual':
                    # Human input
                    try:
                        from_row = int(input("From row (0-7): "))
                        from_col = int(input("From col (0-7): "))
                        to_row = int(input("To row (0-7): "))
                        to_col = int(input("To col (0-7): "))
                        from_pos = (from_row, from_col)
                        to_pos = (to_row, to_col)
                    except ValueError:
                        print("Invalid input")
                        continue
                else:
                    from_pos, to_pos = self.mylzeron_ai_move()
                    print(f"Mylzeron moves: {from_pos} -> {to_pos}")
                    
                if (from_pos[0] == -1 or 
                    not self.make_move(from_pos, to_pos, 'R')):
                    continue
                    
            else:
                print("\nComputer's turn (Black)")
                from_pos, to_pos = self.computer_move(computer_difficulty)
                print(f"Computer moves: {from_pos} -> {to_pos}")
                self.make_move(from_pos, to_pos, 'B')
                if input("Press Enter to continue..."):
                    pass
                    
        # Game over
        print(self.display())
        print("\n" + "=" * 50)
        if self.state.winner == 'R':
            print("  MYLZERON WINS! 🎉")
        elif self.state.winner == 'B':
            print("  COMPUTER WINS")
        else:
            print("  DRAW!")
        print("=" * 50)
        print(f"\nTotal moves: {len(self.state.move_history)}")
        
        return self.state.winner

# Test
if __name__ == "__main__":
    game = Checkers()
    game.play_game(mylzeron_strategy='ai', computer_difficulty='medium')
