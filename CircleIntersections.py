class Circle:
    """
    Represents a circle
    """

    def __init__(self, center_x, center_y, radius):
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
    



def intersection_area(circles):
    """
    Calculates the total area of a list of overlapping circles
    """
    pass