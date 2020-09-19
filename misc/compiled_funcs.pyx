def bezier(control_points, num_of_points):

    def get_points():
        control_x, control_y = zip(*control_points)
        return [
            (
                int(B(control_x, 0, len(control_points) - 1, t / num_of_points)),
                int(B(control_y, 0, len(control_points) - 1, t / num_of_points))
            )
            for t in range(num_of_points)
        ]

    def B(tuple arr, int i, int j, float t) -> float:
        return arr[i] if j == 0 else B(arr, i, j - 1, t) * (1 - t) + B(arr, i + 1, j - 1, t) * t

    return get_points()


def line_collide(list line_1_coords, list line_2_coords) -> tuple:
    cdef float x1, x2, x3, x4, y1, y2, y3, y4

    x1, y1, x2, y2 = line_1_coords
    x3, y3, x4, y4 = line_2_coords

    t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
    u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))

    px = x1 + (t * (x2 - x1))
    py = y1 + (t * (y2 - y1))

    return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else False
