import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from pprint import pprint
from .plan_utils import getKOPFromBUR



class WellTypeIII:
    def __init__(self, TVD, KOP, BUR, reach):
        self.TVD = TVD
        self.KOP = KOP
        self.BUR = BUR
        self.reach = reach

    def calculate(self):
        # Convert build-up rate to radians per meter
        self.BUR_rad = np.deg2rad(self.BUR) / 30
        # Calculate radius of curvature and build-up section length
        self.R = 1 / self.BUR_rad  # Radius of curvature (m)
        dV = self.TVD - self.KOP
        delta_D = self.R - self.reach
        radius_to_reach = np.sqrt(delta_D**2 + dV**2)
        omega = np.arcsin(self.R / radius_to_reach)
        # self.omega = np.pi/2
        tau = np.arctan(delta_D/dV)
        self.theta = omega-tau  # Central angle (radians)
        BU_length = np.round(self.theta * self.R, 5)  # Length of build-up section (m)
        self.aux_data = {
            "radius_to_reach": "%.3f m" % radius_to_reach,
            "omega": "%.3f °" % np.rad2deg(omega),
            "tau": "%.3f °" % np.rad2deg(tau),
            "theta": "%.3f °" % np.rad2deg(self.theta)
        }
        self.kickoff = {
            "MD": self.KOP,
            "TVD": self.KOP,
            "REACH": 0,
            "LENGTH": self.KOP
        }

        # build-up section
        self.build1 = {
            "MD": self.KOP + BU_length,
            "TVD": np.round(self.KOP + self.R * np.sin(self.theta), 5),
            "REACH": np.round(self.R * (1 - np.cos(self.theta)), 5),
            "LENGTH": BU_length
        }

        self.milestones = OrderedDict([
            ("KOP", self.kickoff),
            ("Build-up", self.build1),
            ("Final", self.build1)
        ])

    def printResults(self):
        print("Build-up radius: {:.2f} m".format(self.R))
        print("Build-up angle: {:.2f} deg".format(np.rad2deg(self.theta)))
        pprint(self.aux_data)

        print("---------------------------------------------------------")
        print("{:<15} {:^15} {:^15} {:^15} {:^15}".format("Depth (m)", "TVD", "REACH", "MD", "Length"))
        for key, vals in self.milestones.items():
            print("{:<15} {:^15.3f} {:^15.3f} {:^15.3f} {:^15.3f}".format(
                key, vals["TVD"], vals["REACH"], vals["MD"], vals["LENGTH"]
            ))
        print("---------------------------------------------------------")

    def generatePath(self, tvd = None):
        # Generate the well path
        if tvd is None:
            tvd = np.linspace(0, self.TVD, 200)
        md = np.zeros_like(tvd)
        disp = np.zeros_like(tvd)
        for i, z in enumerate(tvd):
            if z < self.KOP:
                md[i] = z
                disp[i] = 0
            elif z <= self.build1["TVD"]:
                # In the build-up section, solve for theta_z: z = KOP + R * sin(theta_z)
                theta_z = np.arcsin((z - self.KOP) / self.R)
                md[i] = self.KOP + self.R * theta_z
                disp[i] = self.R * (1 - np.cos(theta_z))
        return {"TVD": tvd, "MD": md, "Displacement": disp}

    def plot(self):
        # Create a DataFrame for the trajectory
        plt.figure(figsize=(5, 5))
        ax = plt.gca()
        wellpath = self.generatePath()
        ax.plot(wellpath["Displacement"], wellpath["TVD"],
                 label='Well Trajectory')
        ax.set_xlabel('Horizontal Displacement (m)')
        ax.set_ylabel('True Vertical Depth (m)')
        ax.set_title('Type I Well Trajectory Plan (Input: TVD)')
        Lax = max(self.reach, self.TVD)
        x_spec = [x["REACH"] for x in self.milestones.values()]
        y_spec = [x["TVD"] for x in self.milestones.values()]
        ax.plot(x_spec, y_spec, 'ko', label='Key Points')
        ax.set(xlim=(-0.1*Lax, 1.1*Lax),
                ylim=(-0.1*Lax, 1.1*Lax))
        ax.invert_yaxis()
        ax.legend()
        ax.grid(True)
        plt.show()

