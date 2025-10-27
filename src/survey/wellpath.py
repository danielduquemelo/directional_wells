import numpy as np

# full_trajectory = {
#     "measured_depth": [],
#     "inclination": [],
#     "azimuth": [],
#     "x": [],
#     "y": [],
#     "z": []
#     }

# simplified_trajectory = {
#     "measured_depth": [],
#     "inclination": [],
#     "azimuth": [],
#     "start_point": []
#     }

def minCurvatureSegment(md1, inc1, azim1, md2, inc2, azim2):
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
    return dx, dy, dz

def straigntSegment(md1, md2, inc, azim):
    """"
    calculate the positional increments dx, dy and dz based on a straight 
    inclined segment
    
    arguments:
    md1: float
        measured depth at point 1
    md2: float
        measured depth at point 2
    inc: float
        inclination with respect to vertical (degrees)
    azim: float
        azimuth with respect to north (degrees)
    
    returns:
    
    list: float
        A list with the lengths dx, dy and dz of the segment
    """
    ds = md2-md1
    dx = np.sin(inc)*np.cos(azim)*ds
    dy = np.sin(inc)*np.sin(azim)*ds
    dz = np.cos(inc)*ds
    return dx, dy, dz

def calcCoordinatesFromSimplifiedData(measured_depth, inclination, azimuth, start_point):
    measured_depth = np.array(measured_depth)
    inclination = np.array(inclination)
    azimuth = np.array(azimuth)
    dxyz = np.zeros((len(measured_depth),3))
    for i in range(1, len(measured_depth)):
        md1, md2 = measured_depth[i-1:i+1]
        inc1, inc2 = inclination[i-1:i+1]
        azim1, azim2 = azimuth[i-1:i+1]
        if azim1 == azim2 and inc1 == inc2:
            dxyz[i,:] = straigntSegment(md1, md2, inc2, azim2)
        else:
            dxyz[i,:] = minCurvatureSegment(md1, inc1, azim1, md2, inc2, azim2)
    xyz = np.array([start_point[i] + np.cumsum(dxyz[:,i]) for i in range(3)])
    coordinates = xyz.T
    return coordinates

def serializeFromHydra(data, degrees=True):
    table = np.array(data["table"])
    headers = data["headers"]
    start_point = data["start_point"]
    if degrees:
            thetaConv = lambda x: np.deg2rad(x)
    else:
        thetaConv = lambda x: x
    md = table[:,headers.index("measuredDepth")]
    inc = thetaConv(table[:,headers.index("inclination")])
    azim = thetaConv(table[:,headers.index("azimuth")])
    coords = calcCoordinatesFromSimplifiedData(md, inc, azim, start_point)
    full_trajectory = {"measured_depth": md,
                       "inclination": inc,
                       "azimuth": azim,
                       "x": coords[:,0].tolist(),
                       "y": coords[:,1].tolist(),
                       "z": coords[:,2].tolist()
                       }

    return full_trajectory
        
def getLocalCsysAtVerticalDetpth(full_trajectory, tvd):
    """calculate the local coordinate system in the well path at a given 
    vertical coordinate

    arguments: 
    full trajectory: dict with frull trajectory
    tvd: float with desired vertical coordinate
    
    returns:
    csys: 3x3 ndarray with local coordinate system at the given depth
    point: dict with respective interpolated full trajectory
    """
    interp_point = getDataAtVerticalDepth(full_trajectory, tvd)
    if interp_point is None:
        return None, None
    theta1 = interp_point["inclination"]
    theta2 = interp_point["azimuth"]
    ROTAZIM = np.array(((np.cos(theta2), np.sin(theta2),0),
                        (-np.sin(theta2), np.cos(theta2),0),
                        (0,0,1)))
    ROTINC = np.array(((np.cos(theta1), 0, -np.sin(theta1)),
                        (0,1,0),
                        (np.sin(theta1), 0, np.cos(theta1))))
    v = np.eye(3)
    csys = np.dot(ROTINC,np.dot(ROTAZIM, v))
    return csys, interp_point

def getDataAtVerticalDepth(full_trajectory, tvd):
    if tvd > full_trajectory["z"][-1] or tvd < full_trajectory["z"][0]:
        return None
    interpol = lambda var: np.interp(tvd, full_trajectory["z"], var)
    point = {"measured_depth": interpol(full_trajectory["measured_depth"]),
             "inclination": interpol(full_trajectory["inclination"]),
             "azimuth": interpol(full_trajectory["azimuth"]),
             "x": interpol(full_trajectory["x"]),
             "y": interpol(full_trajectory["y"]),
             "z": tvd
            }
    return point

def getPointCoordinates(point):
    return point["x"], point["y"], point["z"]


    
##
if "__main__" == __name__:
    trajectory = {
    "headers": ["measuredDepth", "inclination", "azimuth"],
    "table": [[1050.0,  3.6, 31.9],    
              [1100.0,  5.7, 32.7],    
              [1150.0,  7.7, 33.9],    
              [1200.0,  9.8, 35.5],    
              [1250.0,  11.8, 37.5],   
              [1300.0,  13.9, 39.8],   
              [1350.0,  16.0, 42.5],   
              [1400.0,  18.0, 45.5],   
              [1450.0,  20.1, 48.9],   
              [1500.0,  22.2, 52.7],   
              [1550.0,  24.2, 56.8],   
              [1600.0,  26.3, 61.2],   
              [1650.0,  28.3, 66.0],   
              [1700.0,  30.4, 71.1],   
              [1750.0,  32.5, 76.5],   
              [1800.0,  34.5, 82.2],   
              [1850.0,  36.6, 88.3],   
              [1900.0,  38.7, 94.6],   
              [1950.0,  40.7, 101.3],  
              [2000.0,  42.8, 108.2],  
              [2050.0,  44.8, 115.4]],
    }

    path = wellPathThreeD()
    path.readFromHydra(trajectory)
    path.calcCoordinates((100,100,1000.))
    csys, xyz0 = path.getLocalCsysAtDetpth(1100)

    from matplotlib import pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    path.addPathTo3DPlot(ax)
    path.addCsysToPlot(ax, csys, xyz0)

    plt.show()



