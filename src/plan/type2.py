import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from pprint import pprint

class WellTypeII:
    def __init__(self, TVD, KOP, BUR, reach, DOR, EOD):
        self.TVD = TVD  # Final vertical depth
        self.KOP = KOP  # Kick-off point
        self.BUR = BUR  # Build-up rate (deg/30m)
        self.reach = reach  # Target horizontal displacement
        self.DOR = DOR  # Drop-off rate (deg/30m)
        self.EOD = EOD  # End of drop-off (TVD)

    def calculate(self):
        # Build-up section
        self.BUR_rad = np.deg2rad(self.BUR) / 30
        self.R = 1 / self.BUR_rad  # Radius of curvature (m)
        # Drop-off section
        self.DOR_rad = np.deg2rad(self.DOR) / 30
        self.R_drop = 1 / self.DOR_rad  # Drop-off radius (m)
        sum_R = self.R + self.R_drop
        dV = self.EOD - self.KOP
        if sum_R > self.reach:
            sumR_to_reach_diff = sum_R - self.reach
            angle_Y = np.arctan(dV / sumR_to_reach_diff)
            angle_Z = np.arccos(np.sin(angle_Y) * sum_R / dV)
            self.theta_BU = angle_Y - angle_Z
            r_type = "R1 + R2 > reach"
        else:
            sumR_to_reach_diff = self.reach - sum_R
            angle_Y = np.arctan(dV / sumR_to_reach_diff)
            angle_Z = np.arccos(np.sin(angle_Y) * sum_R / dV)
            self.theta_BU = np.pi - angle_Y - angle_Z
            r_type = "R1 + R2 < reach"

        self.aux_data = {
            "r_type": r_type,
            # "R - build-up": "%.3f m" % self.R,
            # "R - drop-off": "%.3f m" % self.R_drop,
            # "theta_drop-off": "%.3f deg" % np.rad2deg(self.theta_drop),
            # "theta_build-up": "%.3f deg" % np.rad2deg(self.theta_BU),
            "sumR_to_reach_diff": "%.3f m" % sumR_to_reach_diff,
            "angle_Y": "%.3f deg" % np.rad2deg(angle_Y),
            "angle_Z": "%.3f deg" % np.rad2deg(angle_Z),
            "theta_build-up": "%.3f deg" % np.rad2deg(self.theta_BU),
        }

        # segment_curv_centers = np.sqrt(sumR_to_reach_diff**2 + (self.EOD - self.KOP)**2)
        self.theta_drop = self.theta_BU  # Drop-off angle equals build-up angle for symmetry

        self.kickoff = {
            "TVD": self.KOP,
            "REACH": 0,
            "MD": self.KOP,
            "LENGTH": self.KOP
        }

        # Build-up section calculations
        self.build1 = {
            "MD": self.KOP + self.theta_BU * self.R,
            "TVD": self.KOP + self.R * np.sin(self.theta_BU),
            "REACH": self.R * (1 - np.cos(self.theta_BU)),
            "LENGTH": self.theta_BU * self.R
        }
        # slant section calculations
        tvd_start_drop = self.EOD - self.R_drop * np.sin(self.theta_drop)
        slant_length = (tvd_start_drop - self.build1["TVD"]) / np.cos(self.theta_BU)
        self.slant = {
            "MD": self.build1["MD"] + slant_length,
            "TVD": self.build1["TVD"] + slant_length * np.cos(self.theta_BU),
            "REACH": self.build1["REACH"] + (tvd_start_drop - self.build1["TVD"]) * np.tan(self.theta_BU),
            "LENGTH": slant_length
        }
        # Drop-off section (curves back toward vertical)
        drop_length = self.theta_drop * self.R_drop
        self.drop1 = {
            "MD": self.slant["MD"] + self.theta_drop * self.R_drop,
            "TVD": tvd_start_drop + self.R_drop * np.sin(self.theta_drop),
            "REACH": self.slant["REACH"] + self.R_drop * (1 - np.cos(self.theta_drop)),
            "LENGTH": drop_length
        }

        # Vertical section after drop-off
        self.final = {
            "TVD": self.TVD,
            "REACH": self.reach,
            "MD": self.drop1["MD"] + self.TVD - self.drop1["TVD"],
            "LENGTH": self.TVD - self.drop1["TVD"]
        }

        self.milestones = OrderedDict([
            ("KOP", self.kickoff),
            ("Build-up", self.build1),
            ("Slant section", self.slant),
            ("Drop-off", self.drop1),
            ("Final", self.slant)
        ])

    def printResults(self):
        print("Build-up radius: {:.2f} m".format(self.R))
        print("Drop-off radius: {:.2f} m".format(self.R_drop))
        print("Build-up angle: {:.2f} deg".format(np.rad2deg(self.theta_BU)))
        print("Drop-off angle: {:.2f} deg".format(np.rad2deg(self.theta_drop)))
        pprint(self.aux_data)

        print("---------------------------------------------------------")
        print("{:<15} {:^15} {:^15} {:^15} {:^15}".format("Depth (m)", "TVD", "REACH", "MD", "Length"))
        for key, vals in self.milestones.items():
            print("{:<15} {:^15.3f} {:^15.3f} {:^15.3f} {:^15.3f}".format(
                key, vals["TVD"], vals["REACH"], vals["MD"], vals["LENGTH"]
            ))
        print("---------------------------------------------------------")

    def generatePath(self, tvd=None):
        # Generate the well path for Type II well (with drop-off)
        if tvd is None:
            tvd = np.linspace(0, self.TVD, 300)
        md = np.zeros_like(tvd)
        disp = np.zeros_like(tvd)
        for i, z in enumerate(tvd):
            if z < self.KOP:
                md[i] = z
                disp[i] = 0
            elif z < self.build1["TVD"]:
                # Build-up section
                theta_z = np.arcsin((z - self.KOP) / self.R)
                md[i] = self.KOP + self.R * theta_z
                disp[i] = self.R * (1 - np.cos(theta_z))
            elif z < self.slant["TVD"]:
                # Tangent section
                md[i] = self.build1["MD"] + (z - self.build1["TVD"]) / np.cos(self.theta_BU)
                disp[i] = self.build1["REACH"] + (z - self.build1["TVD"]) * np.tan(self.theta_BU)
            elif z <= self.EOD:
                # Drop-off section (curves back toward vertical)
                theta_drop = np.arcsin((self.EOD - self.slant["TVD"]) / self.R_drop)
                Daux = self.R_drop * np.cos(theta_drop)
                theta_drop_z = np.arcsin((self.EOD - z) / self.R_drop)
                Daux2 = self.R_drop * np.cos(theta_drop_z)
                md[i] = self.slant["MD"] + self.R_drop * (theta_drop - theta_drop_z)
                disp[i] = self.slant["REACH"] + Daux2 - Daux
                # self.R_drop * (np.cos((theta_drop_z - theta_drop)))
            else:
                # Vertical section after drop-off
                md[i] = self.final["MD"] + (z - self.drop1["TVD"])
                disp[i] = self.final["REACH"]

        return {"TVD": tvd, "MD": md, "Displacement": disp}

    def plot(self):
        plt.figure(figsize=(5, 5))
        ax = plt.gca()
        well_path = self.generatePath()
        ax.plot(well_path["Displacement"], well_path["TVD"], label='Well Trajectory')
        ax.set_xlabel('Horizontal Displacement (m)')
        ax.set_ylabel('True Vertical Depth (m)')
        ax.set_title('Type II Well Trajectory Plan (with Drop-off)')
        Lax = max(self.reach, self.TVD)
        ax.set(xlim=(-0.1*Lax, 1.1*Lax),
                ylim=(-0.1*Lax, 1.1*Lax))
        x_spec = [x["REACH"] for x in self.milestones.values()]
        y_spec = [x["TVD"] for x in self.milestones.values()]
        ax.plot(x_spec, y_spec, 'ko', label='Key Points')
        ax.invert_yaxis()
        ax.axis('equal')
        ax.legend()
        ax.grid(True)
        plt.show()

