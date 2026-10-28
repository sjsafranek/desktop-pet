import numpy as np


def generate_constant_speed_trajectory(start, end, speed, dt): 
    # Define start and end points
    p_start = np.array(start)
    p_end = np.array(end)

    # Calculate the total geometric distance between the endpoints
    total_distance = np.linalg.norm(p_end - p_start)
    
    # Determine the total time required to travel the distance at the given speed
    total_time = total_distance / speed

    # Number of steps along the trajectory
    num_steps = int(total_time)

    # Generate straight-line trajectory using linear interpolation
    trajectory = np.linspace(p_start, p_end, num_steps)
    return [[int(point[0]), int(point[1])] for point in trajectory]