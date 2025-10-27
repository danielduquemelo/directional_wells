import numpy as np

def calc_segment(md1, inc1, azim1, md2, inc2, azim2):
    """
    calculate the positional increments of northing, easting, vertical and reach
    for a straight inclined segment based on a mean measured depth between two readings

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
    half_dMD = 0.5 * (md2-md1)
    d_north = half_dMD * (np.sin(inc1) * np.cos(azim1) + np.sin(inc2) * np.cos(azim2))
    d_east = half_dMD *  (np.sin(inc1) * np.sin(azim1) + np.sin(inc2) * np.sin(azim2))
    d_vertical = half_dMD * (np.cos(inc1) + np.cos(inc2))
    d_reach = half_dMD * (np.sin(inc1) + np.sin(inc2))
    return [d_north, d_east, d_vertical, d_reach]
