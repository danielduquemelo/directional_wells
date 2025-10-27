from . import (tangent, balanced_tangent, curvature_radius, mean_angle,
               min_curvature_radius)
import numpy as np
from matplotlib import pyplot as plt

def calc_well_path(data, initial_pos = [0,0,0], method = "min_curvature_radius", display=False):
    data = np.array(data)
    methods = {"min_curvature_radius": min_curvature_radius.calc_segment,
                "mean_angle": mean_angle.calc_segment,
                "curvature_radius": curvature_radius.calc_segment,
                "balanced_tangent": balanced_tangent.calc_segment,
                "tangent": tangent.calc_segment}
    calc_func = methods.get(method)
    if calc_func is None:
        raise ValueError(f"Method '{method}' is not recognized.")
    segments = []
    for i, line in enumerate(data[1:], 1):
        segments.append(calc_func(*data[i-1], *line) +
                        [DogLegSeverity(*data[i-1], *line)])

    segments = np.array(segments)
    reach0 = np.sqrt(initial_pos[0]**2 + initial_pos[1]**2)
    path = np.array(segments)
    path[:,0] = initial_pos[0] + np.cumsum(path[:,0])  # Northing
    path[:,1] = initial_pos[1] + np.cumsum(path[:,1])  # Easting
    path[:,2] = initial_pos[2] + np.cumsum(path[:,2])  # Vertical
    path[:,3] = reach0 + np.sqrt(np.cumsum(path[:,3]))  # Reach
    if display is True:
        data_print = {}
        for i, (dx, dy, dz, dA, DLS) in enumerate(segments, 1):
            real_path = path[i-1]
            data_print[f"Segment {i}"] = {
                "delta_North": np.round(dx,3),
                "delta_East": np.round(dy,3),
                "delta_Vertical": np.round(dz,3),
                "delta_Reach": np.round(dA,3),
                "N": np.round(real_path[0],3),
                "E": np.round(real_path[1],3),
                "TVD": np.round(real_path[2],3),
                "Reach": np.round(real_path[3],3),
                "Dogleg_Severity": np.round(DLS,3)

            }
        from pprint import pprint
        pprint(data_print)
    return segments, path

def get_plot_projection_figs():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # ax1: Vertical Section (Reach vs TVD)
    ax1.set_xlabel('Reach (m)')
    ax1.set_ylabel('TVD (m)')
    ax1.set_title('Vertical Section')
    ax1.invert_yaxis()  # TVD increases downwards

    # ax2: Plan View (Easting vs Northing)
    ax2.set_xlabel('Easting (m)')
    ax2.set_ylabel('Northing (m)')
    ax2.set_title('Plan View')

    return ax1, ax2

def get_plot3D_fig():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Easting (m)')
    ax.set_ylabel('Northing (m)')
    ax.set_zlabel('TVD (m)')
    ax.invert_zaxis()  # Invert Z axis to have TVD increasing downwards
    return ax

def DogLegSeverity(md1, inc1, azim1, md2, inc2, azim2):
    """"
    calculate the dogleg severity based on the minimum curvature formula

    arguments:
    md1: float
        measured depth at point 1
    inc1: float
        inclination with respect to vertical at point 1 (radians)
    azim1: float
        azimuth with respect to north at point 1 (radians)
    md2: float
        measured depth at point 2
    inc2: float
        inclination with respect to vertical at point 2 (radians)
    azim2: float
        azimuth with respect to north at point 2 (radians)

    returns:

    float:
        Dogleg severity in degrees per 30 meters
    """
    dM = md2-md1
    dinc = inc2-inc1
    dazim = azim2-azim1
    beta = 2*np.arcsin(
                    np.sqrt(
                        np.sin(0.5*dinc)**2 +
                        np.sin(inc2)*np.sin(inc1)*np.sin(0.5*dazim)**2))

    DLS = np.rad2deg(beta)/(dM/30)
    return DLS


__all__ = [
    "tangent",
     "balanced_tangent",
     "curvature_radius",
     "mean_angle",
     "min_curvature",
     "min_curvature_radius",
    ]