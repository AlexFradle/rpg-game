from random import randint
from ctypes import CDLL, c_int, py_object


class Vertex:
    def __init__(self, x: int, y: int, wall: bool) -> None:
        self.x = x
        self.y = y
        self.f = 0  # Total cost
        self.g = 0  # Distance from start vertex
        self.h = 0  # Determines shortest distance to end vertex (heuristic)
        self.neighbours = []
        self.previous = None
        # self.wall = True if randint(1, 100) < 20 else False
        self.wall = wall

    def add_neighbours(self, grid: list) -> None:
        """
        Gets adjacent walls
        :param grid: The grid to get neighbours from
        :return: None
        """
        self.neighbours.append(grid[self.y + 1][self.x]) if self.y < len(grid) - 1 else 0
        self.neighbours.append(grid[self.y - 1][self.x]) if self.y > 0 else 0
        self.neighbours.append(grid[self.y][self.x + 1]) if self.x < len(grid[0]) - 1 else 0
        self.neighbours.append(grid[self.y][self.x - 1]) if self.x > 0 else 0


class AStar:
    def __init__(self, cols: int, rows: int, from_file: bool=True, is_maze: bool=True) -> None:
        self.cols = cols
        self.rows = rows
        self.open_set = []  # Unchecked vertices
        self.closed_set = []  # Checked vertices
        self.is_maze = is_maze
        self.from_file = from_file
        self.__a_star_cpp = CDLL("data/a_star.dll")
        self.__a_star_cpp.get_path.argtypes = [c_int, c_int, c_int, c_int]
        self.__a_star_cpp.get_path.restype = py_object
        if from_file:
            self.grid = self.load_from_file(is_maze)
        else:
            self.grid = [[Vertex(j, i, True if randint(1, 100) < 20 else False) for j in range(cols)] for i in range(rows)]

    @staticmethod
    def heuristic(a: Vertex, b: Vertex) -> int:
        """
        Get taxicab distance between two points
        |x1 - x2| + |y1 - y2|
        :param a: First vertex
        :param b: Second vertex
        :return: taxicab distance between a and b
        """
        return abs(a.x - b.x) + abs(a.y - b.y)

    def load_from_file(self, is_maze: bool, fn: str="maze.txt") -> list:
        """
        Load maze to solve from txt file generated by maze_creator.py
        :param is_maze: Determines whether to load a maze or other file
        :param fn: File name to load maze from
        :return: Maze grid
        """
        with open(fn if not is_maze else "data/" + fn) as f:
            maze = [i.replace("\n", "") for i in f.readlines()]
        self.cols = len(maze[0])
        self.rows = len(maze)
        if is_maze:
            grid = [[Vertex(j, i, True if maze[i][j] in ["/", "-", "|"] else False) for j in range(len(maze[0]))] for i in range(len(maze))]
        else:
            grid = [[Vertex(j, i, True if maze[i][j] == "#" else False) for j in range(len(maze[0]))] for i in range(len(maze))]
        return grid

    def solve(self, start: tuple=None, end: tuple=None) -> tuple:
        """
        Solve maze using A*
        :param start: Start position to pathfind from
        :param end: End position to find
        :return: List containing all shortest path vertices and all visited vertices
        """
        # Get all neighbours of vertices in grid
        for row in self.grid:
            for v in row:
                v.add_neighbours(self.grid)

        # Start and end positions
        if start is None or end is None:
            start = self.grid[1 if self.is_maze else 0][1 if self.is_maze else 0]
            end = self.grid[(self.rows - 2) if self.is_maze else self.rows - 1][(self.cols - 2) if self.is_maze else self.cols - 1]
        else:
            start = self.grid[start[0]][start[1]]
            end = self.grid[end[0]][end[1]]

        if self.from_file and not self.is_maze:
            with open("maze.txt") as f:
                maze = [i for i in f.readlines()]
            for i in range(len(maze)):
                if "s" in maze[i]:
                    start_pos = maze[i].find("s")
                    start = self.grid[i][start_pos]
                if "e" in maze[i]:
                    end_pos = maze[i].find("e")
                    end = self.grid[i][end_pos]

        self.open_set.append(start)

        # While all vertices haven't been checked
        while self.open_set:
            smallest = 0
            for i in range(len(self.open_set)):
                if self.open_set[i].f < self.open_set[smallest].f:
                    smallest = i

            # Get current path using the vertices' parent vertex
            path = []
            current = self.open_set[smallest]
            temp = current

            # If current vertex is the end vertex then finish
            if current == end:
                path.append(temp)
                while temp.previous:
                    path.append(temp.previous)
                    temp = temp.previous

                return path, self.closed_set

            # Remove current vertex from open and add it to closed
            self.open_set.remove(current)
            self.closed_set.append(current)

            # Check neighbours for possible routes
            neighbours = current.neighbours
            for i in neighbours:
                neighbour = i
                if neighbour not in self.closed_set and not neighbour.wall:
                    temp_g = current.g + 1  # Neighbour distance from start is one more than current
                    # Trying to get smallest distance
                    if neighbour in self.open_set:
                        if temp_g < neighbour.g:
                            neighbour.g = temp_g
                    else:
                        neighbour.g = temp_g
                        self.open_set.append(neighbour)

                    # Assigning neighbour h and f values
                    neighbour.h = self.heuristic(neighbour, end)
                    neighbour.f = neighbour.g + neighbour.h
                    neighbour.previous = current

    def solve_cpp(self, start: tuple, end: tuple) -> list:
        """
        The C++ implementation of A*
        :param start: Start coords
        :param end: End coords
        :return: List of coords: [(int x, int y), ...]
        """
        path = self.__a_star_cpp.get_path(int(start[0]), int(start[1]), int(end[0]), int(end[1]))
        return path


if __name__ == '__main__':
    # m = AStar(20, 20, False)
    # solved = m.solve()[0]
    # solved = [(i.x, i.y) for i in solved]
    # a = "\n".join([" ".join(["O" if (j, i) in solved else ("#" if m.grid[i][j].wall else " ") for j in range(m.cols)]) for i in range(m.rows)])
    # with open("a_star.txt", "w") as f:
    #     f.write(a)
    a_str = AStar(0, 0).solve()
    a_str_c = AStar(0, 0).solve_cpp((1, 1), (9, 9))
    for a, b in zip(a_str[0], a_str_c):
        print(f"({a.x}, {a.y})  -   ({b[0]}, {b[1]})")
