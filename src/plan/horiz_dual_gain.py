import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from pprint import pprint

class WellHorizontalDualGain:
    def __init__(self, TVD, KOP, BUR1, BUR2, hor_length, reach=None, KOP2=None, max_build=None):
        self.TVD = TVD
        self.KOP = KOP
        self.HOR_SECT = hor_length
        self.BUR1 = np.deg2rad(BUR1)
        self.BUR2 = np.deg2rad(BUR2)

        self.reach = reach
        self.reach_EOB = None
        self.KOP2 = KOP2
        self.max_build = np.deg2rad(max_build) if max_build is not None else None
        self.final_inc = np.pi/2      # final inclination is 90 degrees (horizontal)
        # if reach is not None:
        #     self.reach_EOB = reach - hor_length

        # self.reach = reach - self.reach_EOB

    def calculate(self):
        # Convert build-up rate to radians per meter
        self.BUR1_rad = self.BUR1 / 30
        self.BUR2_rad = self.BUR2 / 30
        # Calculate radius of curvature and build-up section length
        self.R1 = 1 / self.BUR1_rad  # Radius of curvature (m)
        self.R2 = 1 / self.BUR2_rad  # Radius of curvature (m)
        if self.reach is not None:
            self.reach_EOB = self.reach - self.HOR_SECT
            phi = np.arctan2(self.TVD - self.R2 - self.KOP,
                            self.reach_EOB-self.R1)
            curv_center_2_center = np.sqrt((self.reach_EOB - self.R1)**2 +
                                        (self.TVD - self.KOP - self.R2)**2)

            beta = np.arcsin((self.R2 - self.R1)/curv_center_2_center)
            self.theta = np.pi/2 - phi - beta
            delta_V1 = self.R1*np.sin(self.theta)
            delta_D1 = self.R1*(1-np.cos(self.theta))
            delta_V2 = self.R2*(1-np.cos(np.pi/2-self.theta))
            delta_D2 = self.R2*(np.sin(np.pi/2-self.theta))

            self.aux_data = {
                "phi": "%.3f °" % np.rad2deg(phi),
                "beta": "%.3f °" % np.rad2deg(beta),
                "curv_center_2_center": "%.3f m" % curv_center_2_center,
                "R1":  "%.3f m" % self.R1,
                "R2":  "%.3f m" % self.R2,
                "delta_V1": "%.3f m" % delta_V1,
                "delta_D1": "%.3f m" % delta_D1,
                "delta_V2": "%.3f m" % delta_V2,
                "delta_D2": "%.3f m" % delta_D2
            }
        elif self.max_build is not None:
            self.theta = self.max_build
            BU1_length = self.theta * self.R1
            BU2_length = self.R2*(np.pi/2 - self.theta)
            delta_V1 = self.R1*np.sin(self.theta)
            delta_D1 = self.R1*(1-np.cos(self.theta))
            if self.KOP2 is not None:
                delta_V2 = self.TVD - self.KOP2
            else:
                delta_V2 = self.R2*(1-np.cos(np.pi/2 - self.theta))
            # delta_V2 = self.R2*(1-np.cos(np.pi/2 - self.theta))

            delta_D2 = self.R2*(np.sin(np.pi/2-self.theta))
            slant_length = (self.TVD - delta_V1 - delta_V2 - self.KOP)/np.cos(self.theta)
            self.reach = delta_D1 + delta_D2 + slant_length * np.sin(self.theta) + self.HOR_SECT
            self.reach_EOB = self.reach - self.HOR_SECT
            self.aux_data = {
                "R1":  "%.3f m" % self.R1,
                "R2":  "%.3f m" % self.R2,
                "delta_V1": "%.3f m" % delta_V1,
                "delta_D1": "%.3f m" % delta_D1,
                "delta_V2": "%.3f m" % delta_V2,
                "delta_D2": "%.3f m" % delta_D2,
            }
            # self.reach_EOB = (self.R1 * np.cos(self.theta) +
            #                   self.R2 * np.sin(np.pi/2 - self.theta) +
            #                   (self.TVD - self.R1 * np.sin(self.theta) -
            #                    self.R2 * (1 - np.cos(np.pi/2 - self.theta))))


        # build up 1
        BU1_length = self.theta * self.R1
        self.kickoff = {
            "MD": self.KOP,
            "TVD": self.KOP,
            "REACH": 0,
            "LENGTH": self.KOP
        }
        self.build1 = {
            "MD": self.KOP + BU1_length,
            "TVD": self.KOP + self.R1*np.sin(self.theta),
            "REACH": self.R1*(1-np.cos(self.theta)),
            "LENGTH": BU1_length
        }

        # slant section
        slant_length = (self.reach_EOB - delta_D2 - self.build1["REACH"])/np.sin(self.theta)
        self.slant = {
            "MD": self.build1["MD"] + slant_length,
            "TVD": self.build1["TVD"] + slant_length * np.cos(self.theta),
            "REACH": self.build1["REACH"] + slant_length * np.sin(self.theta),
            "LENGTH": slant_length
        }

        # build 2
        BU2_length = self.R2*(np.pi/2 - self.theta)
        self.build2 = {
            "MD": self.slant["MD"] + BU2_length,
            "TVD": self.slant["TVD"] + delta_V2,
            "REACH": self.slant["REACH"] + delta_D2,
            "LENGTH": BU2_length
        }

        # horizontal_section
        self.horizontal_section = {
            "MD": self.build2["MD"] + self.HOR_SECT,
            "TVD": self.TVD,
            "REACH": self.reach,
            "LENGTH": self.HOR_SECT
        }

        self.milestones = OrderedDict([
            ("KOP", self.kickoff),
            ("Build-up 1", self.build1),
            ("slant section", self.slant),
            ("Build up 2", self.build2),
            ("Final", self.horizontal_section)
        ])

    def printResults(self):
        print("Build-up radius: {:.2f} m".format(self.R1))
        print("Build-up radius: {:.2f} m".format(self.R2))
        print("Build-up angle: {:.2f} deg".format(np.rad2deg(self.theta)))
        pprint(self.aux_data)

        print("---------------------------------------------------------")
        print("{:<15} {:^15} {:^15} {:^15} {:^15}".format("Depth (m)", "TVD", "REACH", "MD", "Length"))
        for key, vals in self.milestones.items():
            print("{:<15} {:^15.3f} {:^15.3f} {:^15.3f} {:^15.3f}".format(key, vals["TVD"], vals["REACH"], vals["MD"], vals["LENGTH"]))
        print("---------------------------------------------------------")

    def generatePath(self, tvd=None):
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
            elif z <= self.build1["TVD"]:
                theta_z = np.arcsin((z - self.KOP) / self.R1)
                md[i] = self.KOP + self.R1 * theta_z
                disp[i] = self.R1 * (1 - np.cos(theta_z))
            elif z <= self.slant["TVD"]:
                md[i] = self.build1["MD"] + (z - self.build1["TVD"]) / np.cos(self.theta)
                disp[i] = self.build1["REACH"] + (z - self.build1["TVD"]) * np.tan(self.theta)
            elif z <= self.build2["TVD"]:
                if i <= idx:  # In the build-up section, solve for theta_z: z = KOP + R * sin(theta_z)
                    dV = self.build2["TVD"] - z
                    theta_z = np.arccos(1 - dV/self.R2)
                    dD = self.build2["REACH"] - self.slant["REACH"]
                    md[i] = self.slant["MD"] + self.build2["LENGTH"] - self.R2 * theta_z
                    disp[i] = self.build2["REACH"] - self.R2*np.sin(theta_z)
                else:
                    L_hor = (self.reach-self.reach_EOB)*(i-idx)/(len(tvd)-idx-1)
                    disp[i] = disp[idx] + L_hor
                    md[i] = md[idx] + L_hor
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
        ax.set_title("Horizontal Well (1 build-up) Trajectory Plan (Input: TVD)")
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

