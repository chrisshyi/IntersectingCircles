from typing import List
import math
from copy import deepcopy

class Circle:
    """
    Represents a circle
    """

    def __init__(self, center_x: float, center_y: float, radius: float):
        """
        center_x: x coordinate of center
        center_y: y coordinate of center
        radius: radius of circle
        """
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.y_low = center_y - radius
        self.y_high = center_y + radius
        self.x_0: float = 0.0 # the left intersection point of this circle with the scan line
        self.x_1: float = 0.0 # the right intersection point of this circle with the scan line
    

def circle_distance(circle1: Circle, circle2: Circle):
    return math.sqrt((circle1.center_x - circle2.center_x)**2 + (circle1.center_y - circle2.center_y)**2)

def intersection_area(circles: List[Circle], y_min: float, y_max: float, step: float) -> float:
    """
    Calculates the total area of a list of overlapping circles
    """
    circles.sort(key=lambda circle: circle.center_y, reverse=True) #sort circles in descending ordering of y coordinates
    
    total: float = 0
    row: int = 1 + math.ceil((y_max - y_min) / step)

    while row != 0:
        row -= 1
        y: float = y_min + step * row

        for n in range(len(circles)):
            circle = circles[n]

            if y >= circle.y_high:
                break
            elif y > circle.y_low:
                dx: float = math.sqrt(circle.radius ** 2 - (y - circle.center_y) ** 2)
                circle.x_0 = circle.center_x - dx
                circle.x_1 = circle.center_x + dx

                circles.sort(key=lambda circle: circle.x_0)
            else:
                circles_copy: List[Circle] = deepcopy(circles)
                circles_copy.remove(circle)
                circles = circles_copy
        
        right_end: float = circles[0].x_1
        total += circles[0].x_1 - circles[0].x_0

        for i in range(1, len(circles)):
            circle = circles[i]
            if circle.x_1 <= right_end:
                continue
            total += circle.x_1 - max(circle.x_0, right_end)
            right_end = circle.x_1
    
    return total * step

def main():
    y_min = math.inf
    y_max = -math.inf

    num_circle: int = int(input("Please enter the number of gazes: "))
    radius = float(input("Please enter the radius for the gazes"))
    circles = []
    for n in range(num_circle):
        center_x = float(input("Enter the x coordinate for gaze {}".format(n + 1)))
        center_y = float(input("Enter the y coordinate for gaze {}".format(n + 1)))

        circles.append(Circle(center_x, center_y, radius))
        y_min = min(y_min, center_y - radius)
        y_max = max(y_max, center_y + radius)
    
    step: float = 1 / (1 << 20)
    y_min = math.floor(y_min / step) * step
    area: float = intersection_area(circles, y_min, y_max, step)
    print("The total area of covered by the gazes is {:2f}".format(area))
