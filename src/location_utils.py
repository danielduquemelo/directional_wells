import numpy as np

def reachFromLocation(origin, target):
    """
    Calculate the reach (horizontal displacement) from origin to target.

    Parameters:
    origin (tuple): A tuple (x, y) representing the origin coordinates.
    target (tuple): A tuple (x, y) representing the target coordinates.

    Returns:
    float: The reach (horizontal displacement) from origin to target.
    """
    xy1 = np.array(origin)
    xy2 = np.array(target)
    return np.linalg.norm(xy2 - xy1)

def angleFromLocation(origin, target):
    """
    Calculate the angle (in degrees) from origin to target.

    Parameters:
    origin (tuple): A tuple (x, y) representing the origin coordinates.
    target (tuple): A tuple (x, y) representing the target coordinates.

    Returns:
    float: The angle in degrees from origin to target.
    """
    xy1 = np.array(origin)
    xy2 = np.array(target)
    delta = xy1 - xy2
    angle_rad = np.arctan2(delta[1], delta[0])
    angle_deg = np.degrees(angle_rad)
    return angle_deg if angle_deg >= 0 else angle_deg + 360