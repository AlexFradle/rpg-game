from typing import Iterable, Union, Tuple


def line_collide(line_1_coords: Union[tuple, list], line_2_coords: Union[tuple, list]) -> Union[Tuple[float, float], bool]:
    """
    Line-Line Collision using the equation:


            (x1 - x3)(y3 - y4) - (y1 - y3)(x3 - x4)
        t = ─────────────────────────────────────────────
            (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


              (x1 - x2)(y1 - y3) - (y1 - y2)(x1 - x3)
        u = - ─────────────────────────────────────────────
              (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


        (Px, Py) = (x1 + t(x2 - x1), y1 + t(y2 - y1))
                             or
        (Px, Py) = (x3 + u(x4 - x3), y3 + u(y4 - y3))


    t and u are used to turn the infinite lines into line segments

    t and u can also be used to determine if there is a collision before calculating coords because:
        0.0 ≤ t ≤ 1.0
        0.0 ≤ u ≤ 1.0
    if t or u is outside of this range then there is no collision

    :param line_1_coords: (x1, y1, x2, y2)
    :param line_2_coords: (x3, y3, x4, y4)
    :return: Collision coords
    """
    # Unpacking argument iterable
    x1, y1, x2, y2 = line_1_coords
    x3, y3, x4, y4 = line_2_coords

    # Calculating t and u
    t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
    u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))

    # Calculating intersection coords
    px = x1 + (t * (x2 - x1))
    py = y1 + (t * (y2 - y1))

    return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else False


def colour_lerp(a: Union[tuple, list], b: Union[tuple, list], num_of_cols: int) -> Tuple[float, float]:
    """
    Colour linear interpolation between c1 and c2
    Uses the equation:
        Cr = Ar + t(Br - Ar)
        Cg = Ag + t(Bg - Ag)
        Cb = Ab + t(Bb - Ab)

        0.0 ≤ t ≤ 1.0

        Where:
            A is the start colour,
            B is the end colour,
            C is the interpolated colour

    :param a: Start colour
    :param b: End colour
    :param num_of_cols: Number of divisions to divide the line by
    :return: current interpolated colour
    """
    for t in range(num_of_cols + 1):
        t /= num_of_cols
        c = (a[0] + (t * (b[0] - a[0])), a[1] + (t * (b[1] - a[1])), a[2] + (t * (b[2] - a[2])))
        yield c

