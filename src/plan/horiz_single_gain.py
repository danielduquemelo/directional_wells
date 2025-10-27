import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from pprint import pprint

class WellHorizontalSingleGain:
    def __init__(self, TVD, KOP, reach):
        self.TVD = TVD
        self.KOP = KOP
        self.reach = reach
        self.R = self.TVD - self.KOP  # Radius of curvature (m)
        self.BUR = np.rad2deg(1 / self.R) * 30  # Build-up rate (degrees/30m)

    def calculate(self):
        # Convert build-up rate to radians per meter
        self.BUR_rad = np.deg2rad(self.BUR) / 30
        dV = self.TVD - self.KOP
        self.theta = np.pi/2 # by definition of horizontal well
        BU_length = self.theta * self.R  # Length of build-up section (m)
        self.aux_data = {"Delta V": "%.3f m" % dV,}
        self.kickoff = {
            "MD": self.KOP,
            "TVD": self.KOP,
            "REACH": 0,
            "LENGTH": self.KOP
        }

        self. build1 = {
            "MD": self.KOP + BU_length,
            "TVD": self.TVD,
            "REACH": self.R,
            "LENGTH": BU_length
        }

        self.final = {
            "MD": self.build1["MD"] + self.reach - self.R,
            "TVD": self.TVD,
            "REACH": self.reach,
            "LENGTH": (self.reach - self.R)
        }

        self.milestones = OrderedDict([
            ("KOP", self.kickoff),
            ("build up", self.build1),
            ("Final", self.final)
        ])

    def printResults(self):
        print("Build-up radius: {:.2f} m".format(self.R))
        print("Build-up rate: {:.2f} deg".format(np.rad2deg(self.BUR)))
        print("Build-up angle: {:.2f} deg".format(np.rad2deg(self.theta)))
        pprint(self.aux_data)
        print("---------------------------------------------------------")
        print("{:<15} {:^15} {:^15} {:^15} {:^15}".format("Depth (m)", "TVD", "REACH", "MD", "Length"))
        for key, milestone in self.milestones.items():
            print("{:<15} {:^15.3f} {:^15.3f} {:^15.3f} {:^15.3f}".format(
                key, milestone["TVD"], milestone["REACH"], milestone["MD"], milestone["LENGTH"] ))
        print("---------------------------------------------------------")

    def generatePath(self, tvd = None):
        # Generate the well path
        if tvd is None:
            tvd = np.concatenate((np.linspace(0, self.TVD, 100), np.linspace(self.TVD, self.TVD, 100)))
        md = np.zeros_like(tvd)
        disp = np.zeros_like(tvd)
        idx = np.where(tvd == self.TVD)[0][0]
        for i, z in enumerate(tvd):
            if z < self.KOP:
                md[i] = z
                disp[i] = 0
            elif z <= self.final["TVD"]:
                if i <= idx:# In the build-up section, solve for theta_z: z = KOP + R * sin(theta_z)
                    theta_z = np.arcsin((z - self.KOP) / self.build1["REACH"])
                    md[i] = self.KOP + self.R * theta_z
                    disp[i] = self.R * (1 - np.cos(theta_z))
                else:
                    L_hor = (self.reach-self.R)*(i-idx)/(len(tvd)-idx-1)
                    disp[i] = disp[idx] + L_hor
                    md[i] = self.build1["MD"] + L_hor
        return {"TVD": tvd, "MD": md, "Displacement": disp}

    def plot(self):
        # Create a DataFrame for the trajectory
        plt.figure(figsize=(5, 5))
        ax = plt.gca()
        well_path = self.generatePath()
        ax.plot(well_path["Displacement"], well_path["TVD"],
                 label='Well Trajectory')
        ax.set_xlabel('Horizontal Displacement (m)')
        ax.set_ylabel('True Vertical Depth (m)')
        ax.set_title("Horizontal Well (1 build-up) Trajectory Plan (Input: TVD)")
        Lax = max(self.reach, self.TVD)
        ax.set(xlim=(-0.1*Lax, 1.1*Lax),
                ylim=(-0.1*Lax, 1.1*Lax))
        x_spec = [x["REACH"] for x in self.milestones.values()]
        y_spec = [x["TVD"] for x in self.milestones.values()]
        ax.plot(x_spec, y_spec, 'ok', label='Key Points')
        ax.invert_yaxis()
        ax.legend()
        ax.grid(True)
        plt.show()

