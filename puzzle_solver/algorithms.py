import heapq
from collections import deque

class Node:
    """A node in the search tree for the A* algorithm."""
    def __init__(self, state, parent=None, action=None, g_cost=0):
        self.state = state # 3x3 grid configuration.
        self.parent = parent # link to the Node that came before this one (can rebuild path)
        self.action = action # cost from the start
        self.g_cost = g_cost  # cost from start to current node
        self.h_cost = self.calculate_manhattan_distance() # heuristic cost to goal
        self.f_cost = self.g_cost + self.h_cost  # total estimated cost

    def calculate_manhattan_distance(self):
        """
        Calculates the Manhattan distance heuristic for the current state.
        This is the sum of the distances of each tile from its goal position.
        It's an admissible heuristic because it never overestimates the true cost.
        """
        distance = 0
        goal_positions = {1:(0,0), 2:(0,1), 3:(0,2), 4:(1,0), 5:(1,1), 6:(1,2), 7:(2,0), 8:(2,1), 0:(2,2)}
        
        for r in range(3):
            for c in range(3):
                tile_value = self.state[r][c]
                if tile_value != 0: # does not calculate the blank tile
                    goal_r, goal_c = goal_positions[tile_value]
                    distance += abs(r - goal_r) + abs(c - goal_c)
        return distance

    # the __lt__ method is necessary for the heapq to compare nodes
    def __lt__(self, other):
        return self.f_cost < other.f_cost

def _reconstruct_path(node):
    """Helper function to trace back from the goal node to the start."""
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return path[::-1] # return reversed path (from start to goal)

def _get_neighbors(state, board_class):
    """Helper function to generate valid neighboring states."""
    neighbors = []
    temp_board = board_class()
    
    for move_dir in ['up', 'down', 'left', 'right']:
        # makes a copy of the state to modify for each potential move
        neighbor_state = [row[:] for row in state]
        temp_board.state = neighbor_state
        
        if temp_board.move(move_dir):
            neighbors.append(temp_board.state)
            
    return neighbors

def a_star_solve(initial_board):
    """
    Finds the optimal solution for the 8-puzzle using the A* algorithm.
    """
    # check if the puzzle is solvable
    if not initial_board.is_solvable():
        return None

    start_node = Node(state=initial_board.state)
    goal_state_tuple = tuple(map(tuple, initial_board.goal_state))

    # open_set is a priority queue (min-heap) of nodes to be evaluated
    open_set = [start_node]
    # closed_set stores states that have already been evaluated to avoid cycles
    closed_set = set()

    while open_set:
        # get the node with the lowest f_cost from the priority queue
        current_node = heapq.heappop(open_set)

        # if goal is reached then reconstruct and return the path
        current_state_tuple = tuple(map(tuple, current_node.state))
        if current_state_tuple == goal_state_tuple:
            path = []
            while current_node:
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1] # return reversed path (from start to goal)

        # add the current state to the closed set so we don't visit it again
        closed_set.add(current_state_tuple)

        # explore neighbors (possible moves)
        # create a temporary Board object to use its move logic
        temp_board = type(initial_board)()
        temp_board.state = [row[:] for row in current_node.state]
        blank_r, blank_c = temp_board.find_blank()

        # try all possible moves: up, down, left, right for the blank tile
        for move_dir in ['up', 'down', 'left', 'right']:
            # create a copy of the state to modify
            neighbor_state = [row[:] for row in temp_board.state]
            
            # create a dummy board to test the move
            move_board = type(initial_board)()
            move_board.state = neighbor_state
            
            if move_board.move(move_dir): # if move is valid
                neighbor_state_tuple = tuple(map(tuple, move_board.state))
                
                # if already evaluated this state, skip it
                if neighbor_state_tuple in closed_set:
                    continue

                # the neighbor node
                neighbor_node = Node(
                    state=move_board.state,
                    parent=current_node,
                    g_cost=current_node.g_cost + 1 # each step has a cost of 1
                )
                
                # if neighbor is not in open_set or has a lower f_cost, add it
                found_in_open = any(n for n in open_set if tuple(map(tuple, n.state)) == neighbor_state_tuple and n.f_cost <= neighbor_node.f_cost)

                if not found_in_open:
                    heapq.heappush(open_set, neighbor_node)
    
    return None # should not be reached for a solvable puzzle

def bfs_solve(initial_board):
    """Finds the optimal solution using Breadth-First Search (BFS)."""
    if not initial_board.is_solvable():
        return None

    start_node = Node(state=initial_board.state)
    goal_state_tuple = tuple(map(tuple, initial_board.goal_state))

    # BFS uses a FIFO queue
    queue = deque([start_node])
    visited = {tuple(map(tuple, start_node.state))}

    while queue:
        current_node = queue.popleft()

        if tuple(map(tuple, current_node.state)) == goal_state_tuple:
            return _reconstruct_path(current_node)

        for neighbor_state in _get_neighbors(current_node.state, type(initial_board)):
            neighbor_state_tuple = tuple(map(tuple, neighbor_state))
            
            if neighbor_state_tuple not in visited:
                visited.add(neighbor_state_tuple)
                neighbor_node = Node(state=neighbor_state, parent=current_node)
                queue.append(neighbor_node)
    
    return None

def dfs_solve(initial_board, depth_limit=30):
    """
    Finds a solution using Depth-First Search (DFS) with a depth limit.
    Note: DFS does not guarantee the shortest path.
    """
    if not initial_board.is_solvable():
        return None

    start_node = Node(state=initial_board.state)
    goal_state_tuple = tuple(map(tuple, initial_board.goal_state))

    # DFS uses a LIFO stack
    stack = [start_node]
    visited = set()

    while stack:
        current_node = stack.pop()
        current_state_tuple = tuple(map(tuple, current_node.state))

        if current_state_tuple == goal_state_tuple:
            return _reconstruct_path(current_node)

        # add to visited only when popped to allow revisiting nodes on different paths
        visited.add(current_state_tuple)

        # check depth limit
        if current_node.g_cost < depth_limit:
            for neighbor_state in reversed(_get_neighbors(current_node.state, type(initial_board))):
                neighbor_state_tuple = tuple(map(tuple, neighbor_state))
                if neighbor_state_tuple not in visited:
                    neighbor_node = Node(
                        state=neighbor_state,
                        parent=current_node,
                        g_cost=current_node.g_cost + 1
                    )
                    stack.append(neighbor_node)

    return None