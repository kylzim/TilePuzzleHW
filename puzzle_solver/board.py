import random

class Board:
    def __init__(self):
        # 0 represents the blank space
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.state = [row[:] for row in self.goal_state] # start with solved state

    def find_blank(self):
        """Finds the (row, col) coordinates of the blank tile (0)."""
        for r, row_list in enumerate(self.state):
            for c, value in enumerate(row_list):
                if value == 0:
                    return r, c
        return None, None

    def move(self, direction):
        """
        Moves the blank tile in the given direction if the move is valid.
        Updates self.state.
        Returns True if move was successful, False otherwise.
        """
        blank_r, blank_c = self.find_blank()
        
        # determine the target tile to swap with
        target_r, target_c = blank_r, blank_c
        if direction == 'up':
            target_r += 1
        elif direction == 'down':
            target_r -= 1
        elif direction == 'left':
            target_c += 1
        elif direction == 'right':
            target_c -= 1
        else:
            return False # bad direction

        # check if the target is within the board boundaries
        if 0 <= target_r < 3 and 0 <= target_c < 3:
            # swap the blank tile with the target tile
            self.state[blank_r][blank_c], self.state[target_r][target_c] = \
                self.state[target_r][target_c], self.state[blank_r][blank_c]
            return True
        
        return False

    def shuffle(self, moves=50):
        """
        Shuffles the board by making a number of random, valid moves.
        This ensures the puzzle is always solvable.
        """
        self.state = [row[:] for row in self.goal_state] # start from solved state
        directions = ['up', 'down', 'left', 'right']
        for _ in range(moves):
            random_move = random.choice(directions)
            self.move(random_move) # move() will handle invalid moves

    def is_solvable(self):
        """
        Checks if the puzzle is solvable using the inversion count.
        For an N x N grid (where N=3), a puzzle is solvable if the
        number of inversions is even.
        """
        # flatten the 2D list into a 1D list, ignoring the blank space (0)
        flat_list = [num for row in self.state for num in row if num != 0]
        inversions = 0
        for i in range(len(flat_list)):
            for j in range(i + 1, len(flat_list)):
                if flat_list[i] > flat_list[j]:
                    inversions += 1
        
        # for a 3x3 grid, the puzzle is solvable if the inversion count is even
        return inversions % 2 == 0