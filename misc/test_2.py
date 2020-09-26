# def bezier(control_points, num_of_points):
#
#     def get_points():
#         control_x, control_y = zip(*control_points)
#         return [
#             (
#                 B(control_x, 0, len(control_points) - 1, t / num_of_points),
#                 B(control_y, 0, len(control_points) - 1, t / num_of_points)
#             )
#             for t in range(num_of_points)
#         ]
#
#     def B(arr: tuple, i: int, j: int, t: float) -> float:
#         """
#         Using De Casteljau's algorithm:
#         Gets the one dimensional value of the coords at the provided i value
#         Recurrence relation:
#             B(i, j) = B(i, j - 1) * (1 - t) + B(i + 1, j - 1) * t
#         """
#         if j == 0:
#             return arr[i]
#         else:
#             return B(arr, i, j - 1, t) * (1 - t) + B(arr, i + 1, j - 1, t) * t
#         # return arr[i] if j == 0 else B(arr, i, j - 1, t) * (1 - t) + B(arr, i + 1, j - 1, t) * t
#
#     return get_points()
#
#
# print(bezier([(1, 5), (10, 15), (14, 3), (8, 5)], 1000))

# def line_collide(line_1_coords, line_2_coords) -> tuple:
#     x1, y1, x2, y2 = line_1_coords
#     x3, y3, x4, y4 = line_2_coords
#
#     t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
#     u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
#
#     px = x1 + (t * (x2 - x1))
#     py = y1 + (t * (y2 - y1))
#
#     return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else False
t = "test"