import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from pprint import pprint

class WellTypeI:
    def __init__(self, TVD, KOP, BUR, reach=None, max_build=None):
        self.TVD = TVD
        self.KOP = KOP
        self.BUR = np.deg2rad(BUR)
        self.reach = reach
        self.max_build = np.deg2rad(max_build) if max_build is not None else None
        if reach is None and max_build is None:
            raise ValueError("At least reach or max_build must be provided")


    def calculate(self):
        # Convert build-up rate to radians per meter
        self.BUR_rad = self.BUR / 30
        # Calculate radius of curvature and build-up section length
        self.R = 1 / self.BUR_rad  # Radius of curvature (m)
        if self.max_build is None:
            self.radius_to_reach = np.sqrt((self.R-self.reach)**2 + (self.TVD-self.KOP)**2)
            self.omega = np.arcsin(self.R / self.radius_to_reach)
            self.tau = np.arctan((self.R-self.reach)/(self.TVD - self.KOP))
            self.theta = self.omega-self.tau  # Central angle (radians)
            self.aux_data = {
                "R": "%.3f m" %self.R,
                "radius_to_reach": "%.3f m" %self.radius_to_reach,
                "omega": "%.3f °" % np.rad2deg(self.omega),
                "tau": "%.3f °" % np.rad2deg(self.tau),
                "theta": "%.3f °" % np.rad2deg(self.theta)
            }
        else:
            self.theta = self.max_build
            self.aux_data = {
                "R": "%.3f m" % self.R,
                "theta": "%.3f °" % np.rad2deg(self.theta)
            }

        # build-up section
        self.kickoff = {
            "MD": self.KOP,
            "TVD": self.KOP,
            "REACH": 0,
            "LENGTH": self.KOP
        }
        self.BU_length = self.theta * self.R  # Length of build-up section (m)

        # build-up section
        self.build1 = {
            "MD": self.KOP + self.BU_length,
            "TVD": self.KOP + self.R * np.sin(self.theta),
            "REACH": self.R * (1 - np.cos(self.theta)),
            "LENGTH": self.BU_length
        }

        slant_length = (self.TVD - self.build1["TVD"]) / np.cos(self.theta)
        self.slant = {
            "MD": self.build1["MD"] + slant_length,
            "TVD": self.build1["TVD"] + slant_length * np.cos(self.theta),
            "REACH": self.build1["REACH"] + slant_length * np.sin(self.theta),
            "LENGTH": slant_length
        }

        # self.TVD_end_BU = self.KOP + self.R * np.sin(self.theta)
        # self.disp_end_BU = self.R * (1 - np.cos(self.theta))
        # self.MD_end_BU = self.KOP + self.BU_length
        # slant section length
        # self.slant_length = (self.TVD - self.TVD_end_BU) / np.cos(self.theta)
        # self.MD_target = self.MD_end_BU + self.slant_length
        self.milestones = OrderedDict([
            ("KOP", self.kickoff),
            ("Build-up", self.build1),
            ("Slant section", self.slant),
            ("Final", self.slant)
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
            elif z < self.build1["TVD"]:
                # In the build-up section, solve for theta_z: z = KOP + R * sin(theta_z)
                theta_z = np.arcsin((z - self.KOP) / self.R)
                md[i] = self.KOP + self.R * theta_z
                disp[i] = self.R * (1 - np.cos(theta_z))
            else:
                # In the tangent section
                md[i] = self.build1["MD"] + (z - self.build1["TVD"]) / np.cos(self.theta)
                disp[i] = self.build1["REACH"] + (z - self.build1["TVD"]) * np.sin(self.theta) / np.cos(self.theta)
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
        ax.set(xlim=(-0.1*Lax, 1.1*Lax),
                ylim=(-0.1*Lax, 1.1*Lax))
        x_spec = [x["REACH"] for x in self.milestones.values()]
        y_spec = [x["TVD"] for x in self.milestones.values()]
        ax.plot(x_spec, y_spec, 'ko', label='Key Points')
        ax.invert_yaxis()
        ax.legend()
        ax.grid(True)
        plt.show()

