#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <iterator>
#include <functional>
#include <array>
#include <set>
#define TwoDimVector(dataType) std::vector<std::vector<dataType>>

class Vertex {
    public:
        int x;
        int y;
        bool wall;
        int f = 0;
        int g = 0;
        int h = 0;
        std::vector<std::array<int, 2>> neighbours;
        std::array<int, 2> previous ={NULL, NULL};
        Vertex(int a=0, int b=0, bool w=false){
            x = a;
            y = b;
            wall = w;
        }
};

class AStar {
    public:
        int cols;
        int rows;
        TwoDimVector(Vertex) grid;
        int heuristic(int x1, int y1, int x2, int y2){
            return abs(x1 - x2) + abs(y1 - y2);
        }
        TwoDimVector(Vertex) create_grid(std::vector<std::string> maze){
            TwoDimVector(Vertex) g;
            rows = maze.size();
            cols = maze[0].length();
            g.resize(rows, std::vector<Vertex>(cols, 0));
            for(int i = 0; i < rows; i++){
                for(int j = 0; j < cols; j++){
                    bool is_wall;
                    // Use single quotes for characters
                    if(maze[i][j] == '/' || maze[i][j] == '|' || maze[i][j] == '-'){
                        is_wall = true;
                    }
                    else{
                        is_wall = false;
                    }
                    Vertex vert(j, i, is_wall);
                    g[i][j] = vert;
                }
            }
            return g;
        }
        std::vector<std::array<int, 2>> solve(int start_x, int start_y, int end_x, int end_y){
            std::vector<std::string> str_grid;

            // Get maze from text file
            std::string line;
            std::ifstream file("data/maze.txt");
            if(file.is_open()){
                while(std::getline(file, line)){
                    str_grid.push_back(line);
                }
                file.close();
            }

            grid = create_grid(str_grid);

            // Add neighbpurs
            for(int i = 0; i < rows; i++){
                for(int j = 0; j < cols; j++){
                    int x = grid[i][j].x, y = grid[i][j].y;
                    std::array<int, 2> arr;
                    if(y < rows - 1){
                        arr[0] = x;
                        arr[1] = y + 1;
                        grid[i][j].neighbours.push_back(arr);
                    }
                    if(y > 0){
                        arr[0] = x;
                        arr[1] = y - 1;
                        grid[i][j].neighbours.push_back(arr);
                    }
                    if(x < cols - 1){
                        arr[0] = x + 1;
                        arr[1] = y;
                        grid[i][j].neighbours.push_back(arr);
                    }
                    if(x > 0){
                        arr[0] = x - 1;
                        arr[1] = y;
                        grid[i][j].neighbours.push_back(arr);
                    }
                }
            }

            // Start and end positions
            std::array<int, 2> start = {start_x, start_y};
            std::array<int, 2> end = {end_x, end_y};


            // Create open set
            std::vector<std::array<int, 2>> open_set;
            std::set<std::array<int, 2>> closed_set;
            open_set.push_back(start);

            // Start main solving loop
            int smallest;
            while(open_set.size() > 0){
                smallest = 0;
                for(int i = 0; i < open_set.size(); i++){
                    if(grid[open_set[i][1]][open_set[i][0]].f < grid[open_set[smallest][1]][open_set[smallest][0]].f){
                        smallest = i;
                    }
                }
                // Create 
                std::vector<std::array<int, 2>> path;
                std::array<int, 2> current = {open_set[smallest][0], open_set[smallest][1]};
                std::array<int, 2> temp = {current[0], current[1]};

                // Return if the current and end positions are the same
                if (current[0] == end[0] && current[1] == end[1]){
                    path.push_back(temp);

                    // Get path using the previous positions
                    while(grid[temp[1]][temp[0]].previous[0] && grid[temp[1]][temp[0]].previous[1]){
                        path.push_back(grid[temp[1]][temp[0]].previous);
                        int tx = grid[temp[1]][temp[0]].previous[0];
                        int ty = grid[temp[1]][temp[0]].previous[1];
                        temp[0] = grid[ty][tx].x;
                        temp[1] = grid[ty][tx].y;
                    }
                    return path;
                }
                
                open_set.erase(std::remove(open_set.begin(), open_set.end(), current), open_set.end());
                closed_set.insert(current);

                std::vector<std::array<int, 2>> neighbours = grid[current[1]][current[0]].neighbours;

                for(int i = 0; i < neighbours.size(); i++){
                    // Create neighbours array
                    std::array<int, 2> neighbour = {neighbours[i][0], neighbours[i][1]};

                    // if neighbours not in closed set and not a wall
                    if(closed_set.find(neighbour) == closed_set.end() && grid[neighbour[1]][neighbour[0]].wall == false){
                        int temp_g = grid[current[1]][current[0]].g + 1;

                        // if neighbour in open set
                        if(std::find(open_set.begin(), open_set.end(), neighbour) != open_set.end()){
                            if(temp_g < grid[neighbour[1]][neighbour[0]].g){
                                grid[neighbour[1]][neighbour[0]].g = temp_g;
                            }
                        }
                        else{
                            grid[neighbour[1]][neighbour[0]].g = temp_g;
                            open_set.push_back(neighbour);
                        }
                        // Set h using heuristic
                        grid[neighbour[1]][neighbour[0]].h = heuristic(neighbour[0], neighbour[1], end[0], end[1]);

                        // Set f with the sum of g and h
                        grid[neighbour[1]][neighbour[0]].f = grid[neighbour[1]][neighbour[0]].g + grid[neighbour[1]][neighbour[0]].h;

                        // Set previous positions
                        grid[neighbour[1]][neighbour[0]].previous[0] = current[0];
                        grid[neighbour[1]][neighbour[0]].previous[1] = current[1];
                    }
                }
            }
            // Return empty array if the maze couldn't be solved
            std::vector<std::array<int, 2>> not_solved;
            return not_solved;
        }
};


extern "C" {
    PyObject *get_path(int sx, int sy, int ex, int ey){
        Py_Initialize();
        AStar a_star;
        std::vector<std::array<int, 2>> path_int = a_star.solve(sx, sy, ex, ey);
        PyObject *py_path = PyList_New(0);
        for(int i = 0; i < path_int.size(); i++){
            // tuple in the form (int, int)
            PyObject *t = Py_BuildValue("(ii)", path_int[i][0], path_int[i][1]);
            PyList_Append(py_path, t);
        }
        return py_path;
    }
}


int main(){
    // AStar a_star;
    // std::vector<std::array<int, 2>> path_int = a_star.solve(1, 1, 9, 9);
    // for(int i = 0; i < path_int.size(); i++){
    //     std::cout << "(" << path_int[i][1] << ", " << path_int[i][0] << ")" << std::endl;
    // }
    return 0;
}