import numpy as np

def calc_segment(md1, inc1, azim1, md2, inc2, azim2):
    """"
    calculate the positional increments dN, dE and dV based on a
    straight inclined segment

    arguments:
    dMD: float
        measured depth increment
    inc: float
        inclination at point 2 with respect to vertical (radians)
    azim: float
        azimuth at point 2 with respect to north (radians)

    returns:

    list: float
        A list with the lengths dN, dE and dV of the segment
    """
    dMD = md2 - md1
    d_north = dMD * np.sin(inc2) * np.cos(azim2)
    d_east = dMD * np.sin(inc2) * np.sin(azim2)
    d_vertical = dMD * np.cos(inc2)
    d_reach = dMD * np.sin(inc2)
    return [d_north, d_east, d_vertical, d_reach]