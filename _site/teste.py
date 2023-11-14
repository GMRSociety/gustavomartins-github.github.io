import numpy as np
import string
from tabulate import tabulate

class NQueenSolver:

    def __init__(self, size_of_board):
        self.size = size_of_board       
        self.columns = []
        self.num_of_places = 0
        self.num_of_backjumps = 0
        self.conflict_set = {new_list: [] for new_list in range(self.size)}

    def place_queen(self, starting_row=0):
        if len(self.columns) == self.size:
            print(f"Board size: {self.size} x {self.size}")
            print(f"{self.num_of_places} attempts were made to place the Queens which include {self.num_of_backjumps} backjumps.")
            return self.columns
        else:
            for row in range(starting_row, self.size):
                if self.is_safe(len(self.columns), row) is True:
                    self.columns.insert(len(self.columns),row)
                    self.num_of_places += 1
                    return self.place_queen()

            max_jump = self.conflict_set[len(self.columns)]
            max_jump = set(max_jump)
            last_row = max(max_jump)
            self.num_of_backjumps += 1
            for i in range(last_row+1, self.size):
                self.conflict_set[i] = []
            previous_variable = self.columns[last_row]
            self.columns = self.columns[:last_row]
            return self.place_queen(starting_row = previous_variable+1)

    def is_safe(self, col, row):
        for conflict_col, conflict_row in enumerate(self.columns):
            if row == conflict_row:                
                self.conflict_set[col].append(conflict_col)         
                return False
            elif abs(conflict_row - row) == abs(conflict_col - col):
                self.conflict_set[col].append(conflict_col)            
                return False
        return True

size = input("Enter the size of the board:")
n = int(size)
queens = NQueenSolver(n)
queens.place_queen(0)
board = np.full((n, n), " ")
for col_queen, row_queen in enumerate(queens.columns):
    board[row_queen][col_queen] = 'Q'   
headers = list(string.ascii_uppercase)
headers = headers[:n]
table = tabulate(board, headers, showindex=range(0,n), tablefmt="fancy_grid")
print(table)
