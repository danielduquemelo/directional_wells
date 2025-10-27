import numpy as np

def getKOPFromBUR(reach, TVD, BUR):
    BUR_rad = np.deg2rad(BUR) / 30
    R = 1 / BUR_rad  # Radius of curvature (m)
    delta_D = R - reach
    theta = np.arccos(delta_D/R)  # Central angle (radians)
    KOP = TVD - R * np.sin(theta)
    return KOP

def getKOPFromInclination(reach, TVD, inc):
    theta = np.deg2rad(inc)
    dV = np.tan(theta) * reach
    KOP = TVD - dV
    R = dV / np.sin(theta)
    return KOP, R