import numpy as np


def calc_inclination_and_direction(beta, gamma, inc1):
    """
    beta: tool deflection (dogleg) in radians
    gamma: tool orientation in radians
    inc1: initial inclination in radians

    returns:
    delta epsilon (change in direction) in radians,
    inc2 (final inclination) in radians
    """

    denom = np.sin(inc1) + np.tan(beta) * np.cos(gamma) * np.cos(inc1)
    depsilon = np.arctan((np.tan(beta) * np.sin(gamma))/denom)
    inc2 = np.arccos(np.cos(inc1)*np.cos(beta) - np.sin(beta)*np.cos(gamma)*np.sin(inc1))
    return depsilon, inc2


def calc_tool_angle(beta, inc1, inc2):
    """
    beta: tool angle deflection (dogleg) in radians
    inc1: initial inclination in radians
    inc2: final inclination in radians

    returns: gamma tool angle in radians
    """
    gamma = np.arccos((np.cos(inc1)*np.cos(beta) - np.cos(inc2)) / (np.sin(inc1)*np.sin(beta)))
    return gamma


def calc_max_direction_change(beta, inc1):
    """
    inc1: initial inclination in radians
    beta: tool dogleg severity in radians per length
    length: length over which the dogleg severity is applied (default 30m)

    returns: maximum change in direction in radians
    """
    from scipy.optimize import fmin
    f = lambda x: calc_inclination_and_direction(beta, x, inc1)
    res_x = fmin(lambda x: -f(x)[0], x0=0, disp=False)
    gamma = res_x[0]
    de_max = f(gamma)[0]
    return gamma, de_max


