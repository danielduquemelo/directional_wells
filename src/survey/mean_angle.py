import numpy as np

def calc_segment(md1, inc1, azim1, md2, inc2, azim2):
    """
    calculate the positional increments of northing, easting, vertical and reach
    for a straight line based on the mean angle between two readings

    arguments:
    md1: float
        measured depth at point 1
    inc1: float
        inclination at point 1 with respect to vertical (radians)
    azim1: float
        azimuth at point 1 with respect to north (radians)
    md2: float
        measured depth at point 2
    inc2: float
        inclination at point 2 with respect to vertical (radians)
    azim2: float
        azimuth at point 2 with respect to north (radians)

    returns:

    list: float
        A list with the lengths northing, easting, vertical and reach segment
    """
    half_inc = 0.5 * (inc2+inc1)
    half_azim = 0.5 * (azim2+azim1)
    dMD = (md2-md1)

    d_north = dMD * (np.sin(half_inc) * np.cos(half_azim))
    d_east = dMD * (np.sin(half_inc) * np.sin(half_azim))
    d_vertical = dMD * (np.cos(half_inc))
    d_reach = dMD * (np.sin(half_inc))
    return [d_north, d_east, d_vertical, d_reach]
