import numpy as np


def calc_segment(md1, inc1, azim1, md2, inc2, azim2):
    """"
    calculate the positional increments dx, dy and dz based on the
    minimum curvature formula

    arguments:
    md1: float
        measured depth at point 1
    inc1: float
        inclination with respect to vertical at point 1 (degrees)
    azim1: float
        azimuth with respect to north at point 1 (degrees)
    md2: float
        measured depth at point 2
    inc2: float
        inclination with respect to vertical at point 2 (degrees)
    azim2: float
        azimuth with respect to north at point 2 (degrees)

    returns:

    list: float
        A list with the lengths dx, dy and dz of the segment
    """
    ds = md2-md1
    dinc = inc2-inc1
    dazim = azim2-azim1
    slantAngle = 2*np.arcsin(
                    np.sqrt(
                        np.sin(0.5*dinc)**2 +
                        np.sin(inc2)*np.sin(inc1)*np.sin(0.5*dazim)**2))
    RF = (ds/slantAngle)*np.tan(0.5*slantAngle)
    dx = (np.sin(inc1)*np.cos(azim1)+
          np.sin(inc2)*np.cos(azim2))*RF
    dy = (np.sin(inc1)*np.sin(azim1)+
          np.sin(inc2)*np.sin(azim2))*RF
    dz = (np.cos(inc1)+np.cos(inc2))*RF
    d_reach = np.sqrt(dx**2 + dy**2)
    return [dx, dy, dz, d_reach]


# def min_curvature_survey(md, inc, azim):