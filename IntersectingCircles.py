from typing import List
import math
import random
import os
import csv


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
        self.x_0: float = 0.0  # the left intersection point of this circle with the scan line
        self.x_1: float = 0.0  # the right intersection point of this circle with the scan line

    def __eq__(self, other):
        return self.center_x == other.center_x and self.center_y == other.center_y and self.radius == other.radius


def circle_distance(circle1: Circle, circle2: Circle):
    return math.sqrt((circle1.center_x - circle2.center_x)**2 + (circle1.center_y - circle2.center_y)**2)


def intersection_area(circles: List[Circle], y_min: int, y_max: int, step: float) -> float:
    """
    Calculates the total area of a list of overlapping circles
    """
    def intersect(circle, y):
        """
        Returns the intersection points of a circle with a horizontal line y = y
        :param circle: The circle of interest
        :param y: the horizontal line y = y
        :return: the x coordinates of the two intersection points as a tuple
        """
        dx: float = math.sqrt(circle.radius ** 2 - (y - circle.center_y) ** 2)
        return circle.center_x - dx, circle.center_x + dx
    
    total: float = 0

    for row in range(y_min, y_max + 1):
        print("{} rows left".format(y_max + 1 - row))
        right_end = -math.inf
        y_cur = step * row

        for (x0, x1) in sorted(intersect(circle, y_cur)
                               for circle in circles if abs(y_cur - circle.center_y) < circle.radius):
            if x1 < right_end:
                continue
            total += x1 - max(right_end, x0)
            right_end = x1

    return total * step


def is_inside_circle(circles, point):
    """
    :param circles: a list of Circle objects
    :param point: a tuple representing a 2D point, (x coordinate, y coordinate)
    :return: True if the point is within one or more of the circles, False if otherwise
    """
    for circle in circles:
        if math.sqrt(((point[0] - circle.center_x) ** 2) + ((point[1] - circle.center_y) ** 2)) < circle.radius:
            return True
    return False


def monte_carlo_sampling(x_min, y_min, x_max, y_max, num_trials, circles, output_file):
    """
    Estimates the area bound by a list of circles using Monte Carlo Sampling
    :param x_min: the lowest x coordinate bound by the circles
    :param y_min: the lowest y coordinate bound by the circles
    :param x_max: the highest x coordinate bound by the circles
    :param y_max: the highest y coordinate bound by the circles
    :param num_trials: number of trials
    :param circles: list of Circle objects
    :param output_file: the output file to write the calculated data to
    :return: estimated area, standard deviation of the estimated area
    """
    bound_box_area = (x_max - x_min) * (y_max - y_min)

    num_hits = 0
    num_tries = 0

    while True:
        if is_inside_circle(circles, (random.uniform(x_min, x_max), random.uniform(y_min, y_max))):
            num_hits += 1

        num_tries += 1

        if num_tries == num_trials:
            estimated_proportion = num_hits / num_trials
            estimated_area = bound_box_area * estimated_proportion
            std_dev = bound_box_area * math.sqrt(estimated_proportion * (1 - estimated_proportion) / num_trials)

            result_str = "{:.4f} +/- {:.4f} ({} samples)\n".format(estimated_area, std_dev, num_tries)
            print(result_str)
            output_file.write(result_str)
            if std_dev * 3 <= (estimated_area / 100):  # adjust this error to the desired level of precision
                break
            num_trials *= 2


def main():

    circles = []

    gazes_data = {}

    trial_min_max_data = {}

    data_file_path = os.path.abspath(input("Please enter the path to the data file\n"))
    out_file_path = os.path.abspath(input("Please enter the path to the desired output file\n"))

    curr_trial_num = 1
    trial_num = 1

    file_num = 0
    curr_file_num = 0

    y_min = math.inf
    y_max = -math.inf

    x_min = math.inf
    x_max = -math.inf

    with open(data_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        row_num = 0
        for row in csv_reader:
            # consume the first row which contains the headers for the columns
            if row_num == 0:
                row_num += 1
                continue

            trial_num = int(row[1])
            file_num = int(row[0])
            if (curr_file_num, curr_trial_num) != (file_num, trial_num):
                trial_min_max_data[(curr_file_num, curr_trial_num)] = {}
                trial_min_max_data[(curr_file_num, curr_trial_num)]['x_min'] = x_min
                trial_min_max_data[(curr_file_num, curr_trial_num)]['x_max'] = x_max
                trial_min_max_data[(curr_file_num, curr_trial_num)]['y_min'] = y_min
                trial_min_max_data[(curr_file_num, curr_trial_num)]['y_max'] = y_max

                curr_trial_num = trial_num
                curr_file_num = file_num

                y_min = math.inf
                y_max = -math.inf

                x_min = math.inf
                x_max = -math.inf

            center_x = float(row[4])
            center_y = float(row[5])
            radius = float(row[6]) / 2

            if trial_num not in gazes_data:
                gazes_data[(curr_file_num, curr_trial_num)] = []
            gazes_data[(curr_file_num, curr_trial_num)].append(Circle(center_x, center_y, radius))

            y_min = min(y_min, center_y - radius)
            y_max = max(y_max, center_y + radius)

            x_min = min(x_min, center_x - radius)
            x_max = max(x_max, center_x + radius)

    # add the data for the last trial number
    trial_min_max_data[(file_num, trial_num)] = {}
    trial_min_max_data[(file_num, trial_num)]['x_min'] = x_min
    trial_min_max_data[(file_num, trial_num)]['x_max'] = x_max
    trial_min_max_data[(file_num, trial_num)]['y_min'] = y_min
    trial_min_max_data[(file_num, trial_num)]['y_max'] = y_max

    with open(out_file_path, 'w') as output_file:
        for (file_num, trial_num) in gazes_data:

            print('file num: ' + str(file_num))
            print('trial ' + str(trial_num))
            for x in range(3):
                output_file.write("-----------------")
            print('\n')
            min_max_data = trial_min_max_data[(file_num, trial_num)]
            # Adjust the step size up or down if less or more precision is desired, respectively
            step: float = 1 / (1 << 12)
            y_min_step = int(math.floor(min_max_data['y_min'] / step))
            y_max_step = int(math.ceil(min_max_data['y_max'] / step))
            area: float = intersection_area(gazes_data[(file_num, trial_num)], y_min_step, y_max_step, step)
            output_file.write("File Number: " + str(file_num) + '\n')
            output_file.write("Trial Number: " + str(trial_num) + '\n')
            scanline_result_str = \
                "The total area of covered by the gazes is {:2f}, based on the scanline method\n".format(area)
            print(scanline_result_str)
            output_file.write(scanline_result_str)
            monte_carlo_sampling(min_max_data['x_min'], min_max_data['y_min'],
                                 min_max_data['x_max'], min_max_data['y_max'],
                                 65536, gazes_data[(file_num, trial_num)], output_file)


if __name__ == "__main__":
    main()
