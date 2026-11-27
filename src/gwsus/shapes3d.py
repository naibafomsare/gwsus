# Disable warning about deprecated package used by VPython.
# Remove once VPython has been updated.
import warnings

warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API.*",
    category=UserWarning,
)

import vpython as vp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

plt.style.use("dark_background")

# Extract the list of hex codes from the current style's color cycle
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

# Convert a specific hex to RGB
# rgb_value = to_rgb(colors[0])

# --------- Parent classes for bodies and links -----------#

# The difference between these two classes is that links don't use the `up_new` and `up` parameters,
# which means that torsion of the links is not depicted in the animation.


class BasicBodyShape:
    def update_pos(self, cm_pos_new, axis_new, up_new):
        geo_pos_new = cm_pos_new + self.geo_pos_local
        self.shape.pos = vp.vec(*geo_pos_new)
        self.shape.axis = vp.vec(*axis_new)
        self.shape.up = vp.vec(*up_new)


class BasicLinkShape:
    def update_pos(self, pos_new, axis_new):
        self.shape.pos = vp.vec(*pos_new)
        self.shape.axis = vp.vec(*axis_new)


# --------- Body children classes -------------#


class CubeShape(BasicBodyShape):
    def __init__(self, pos, axis, up, **kwargs):
        side = 30e-3
        color = vp.vec(*to_rgb(colors[0]))
        self.shape = vp.compound(
            [
                vp.box(
                    pos=vp.vec(*pos),
                    axis=vp.vec(*axis),
                    up=vp.vec(*up),
                    length=side,
                    height=side,
                    width=side,
                    color=color,
                    visible=False,
                )
            ],
            visible=False,
        )
        self.update_pos(pos, axis, up)
        self.shape.visible = True


class MirrorShape(BasicBodyShape):
    def __init__(self, cm_pos, axis, up, **kwargs):
        self.geo_pos_local = np.array([0, 0, 0])
        geo_pos = cm_pos + self.geo_pos_local
        diameter = 250e-3
        length = 151.399e-3
        color = vp.vec(*to_rgb(colors[0]))
        self.shape = vp.compound(
            [
                vp.cylinder(
                    pos=vp.vec(-length / 2, 0, 0),
                    axis=vp.vec(length, 0, 0),
                    up=vp.vec(0, 0, 1),
                    radius=diameter / 2,
                    opacity=0.6,
                    color=color,
                    visible=False,
                )
            ],
            pos=vp.vec(*geo_pos),
            visible=False,
        )
        self.update_pos(cm_pos, axis, up)
        self.shape.visible = True


class RecoilMassShape(BasicBodyShape):
    def __init__(self, cm_pos, axis, up, **kwargs):
        self.geo_pos_local = np.array([0, 0, 0])
        geo_pos = cm_pos + self.geo_pos_local
        length = 186e-3
        outer_shape = vp.shapes.circle(radius=154e-3)
        inner_shape = vp.shapes.circle(radius=134e-3)  # This will be the hole
        difference = [outer_shape, inner_shape]
        color = vp.vec(255 / 255, 105 / 255, 97 / 255)
        # color=vp.vec( *to_rgb(colors[1]) )
        # Extrude with subtraction, the inner_shape is subtracted from outer_shape
        self.shape = vp.compound(
            [
                vp.extrusion(
                    path=[vp.vec(-length / 2, 0, 0), vp.vec(length, 0, 0)],
                    shape=difference,
                    opacity=0.4,
                    color=color,
                    visible=False,
                )
            ],
            pos=vp.vec(*geo_pos),
            visible=False,
        )
        self.update_pos(cm_pos, axis, up)
        self.shape.visible = True


class IntermediateMassShape(BasicBodyShape):
    def __init__(self, cm_pos, axis, up, **kwargs):
        self.geo_pos_local = np.array([0, 0, 7e-3])
        geo_pos = cm_pos + self.geo_pos_local
        width_IM = 230e-3
        height_IM = 150e-3
        color = vp.vec(*to_rgb(colors[0]))

        # With a sphare at the center
        # center = vp.sphere( pos=vp.vec(*geo_pos), radius=0.01, color=vp.color.red )
        # self.shape = vp.compound( [ center, vp.box( pos = vp.vec(*geo_pos) ,
        #                                     axis = vp.vec(*axis) ,
        #                                     up = vp.vec(*up) ,
        #                                     length =  width_IM ,
        #                                     height = width_IM ,
        #                                     width = height_IM ,
        #                                     color = color ) ] , opacity=0.3 , visible = True )

        self.shape = vp.compound(
            [
                vp.box(
                    pos=vp.vec(0, 0, 0),  # pos = vp.vec(*geo_pos) ,
                    axis=vp.vec(*axis),
                    up=vp.vec(*up),
                    length=width_IM,
                    height=width_IM,
                    width=height_IM,
                    color=color,
                    visible=False,
                )
            ],
            pos=vp.vec(*geo_pos),
            opacity=0.3,
            visible=False,
        )

        # print('IM size:', self.shape.size )
        # print('IM geo_pos:', geo_pos )

        self.update_pos(cm_pos, axis, up)
        self.shape.visible = True


# -------- IRM ----------#


class IntermediateRecoilMassShape(BasicBodyShape):
    def __init__(self, cm_pos, axis, up, **kwargs):

        # Position of geometrical center w.r.t. center of mass
        self.geo_pos_local = np.array([0, 0, -25.5e-3])

        geo_pos = cm_pos + self.geo_pos_local
        # Dimensions of box
        height = 181e-3
        length = 346e-3
        width = length
        thick = 8e-3
        color = vp.color.cyan

        # +Vertical
        ver_plus = vp.box(
            pos=vp.vec(0, height / 2 - thick / 2, 0),
            up=vp.vec(0, 0, 1),
            length=length,
            width=thick,
            height=width,
            visible=False,
        )

        # +Longitudinal
        lon_plus = vp.box(
            pos=vp.vec(length / 2 - thick / 2, -thick / 2, 0),
            up=vp.vec(0, 0, 1),
            length=thick,
            width=height - thick,
            height=width,
            visible=False,
        )

        # -Longitudinal
        lon_minus = vp.box(
            pos=vp.vec(-length / 2 + thick / 2, -thick / 2, 0),
            up=vp.vec(0, 0, 1),
            length=thick,
            width=height - thick,
            height=width,
            visible=False,
        )

        # +Transverse
        trv_plus = vp.box(
            pos=vp.vec(0, -thick / 2, width / 2 - thick / 2),
            up=vp.vec(0, 0, 1),
            length=length - 2 * thick,
            width=height - thick,
            height=thick,
            visible=False,
        )

        # -Transverse
        trv_minus = vp.box(
            pos=vp.vec(0, -thick / 2, -width / 2 + thick / 2),
            up=vp.vec(0, 0, 1),
            length=length - 2 * thick,
            width=height - thick,
            height=thick,
            visible=False,
        )

        # With a sphere at the center
        # center = vp.sphere( pos=vp.vec(0,0,0), radius=0.01, color=vp.color.green )
        # self.shape = vp.compound( [ center, ver_plus, lon_plus, lon_minus, trv_plus, trv_minus ], opacity=0.3, visible=True, color=color )

        self.shape = vp.compound(
            [ver_plus, lon_plus, lon_minus, trv_plus, trv_minus],
            pos=vp.vec(*geo_pos),
            opacity=0.3,
            visible=False,
            color=color,
        )

        # print('IRM size:', self.shape.size )
        # print('IRM geo_pos:', geo_pos )

        self.update_pos(cm_pos, axis, up)
        self.shape.visible = True


class GroundShape:
    pass


# ---------- Link children classes ---------------#


class WireShape(BasicLinkShape):
    def __init__(self, pos, axis, **kwargs):
        diameter = 6e-3
        color = vp.color.white
        self.shape = vp.cylinder(
            pos=vp.vec(*pos),
            axis=vp.vec(*axis),
            radius=diameter / 2,
            color=color,
            visibility=False,
        )
        self.update_pos(pos, axis)
        self.shape.visible = True


class SpringShape(BasicLinkShape):
    def __init__(self, pos, axis, **kwargs):

        # According to the minimum dimension
        # of the box surrounding the object
        # that hangs from the spring.
        diameter = kwargs["min_dim"] * 0.5

        coil_density = 5 / 60e-3  # coils per unit length
        coils = int(coil_density * np.linalg.norm(axis))  # Number of windings
        color = vp.color.white
        self.shape = vp.helix(
            pos=vp.vec(*pos),
            axis=vp.vec(*axis),
            radius=diameter / 2,
            coils=coils,
            color=color,
        )
        self.update_pos(pos, axis)
        self.shape.visible = True


# ----------- For GAS filter -------------#


class GASFilterShape(BasicBodyShape):
    def __init__(self, cm_pos, axis, up, **kwargs):

        # Position of geometrical center w.r.t. center of mass
        self.geo_pos_local = np.array([0, 0, 0])

        geo_pos = cm_pos + self.geo_pos_local
        upper_radius = 609.257e-3 / 2
        lower_radius = 362.000e-3
        cone_height = 142e-3
        base_height = 30.5e-3
        color = vp.vec(255 / 255, 105 / 255, 97 / 255)
        # color=vp.vec( *to_rgb(colors[1]) )

        cone = vp.extrusion(
            path=[vp.vec(0, 0, -cone_height / 2), vp.vec(0, 0, cone_height / 2)],
            shape=vp.shapes.circle(radius=lower_radius),
            scale=[1, upper_radius / lower_radius],
            color=color,
            visible=False,
        )

        cone.rotate(axis=vp.vec(1, 0, 0), angle=-vp.pi / 2)

        disc = vp.extrusion(
            path=[vp.vec(0, 0, -base_height / 2), vp.vec(0, 0, base_height / 2)],
            shape=vp.shapes.circle(radius=lower_radius),
            scale=[1, 1],
            color=color,
            visible=False,
        )

        disc.rotate(axis=vp.vec(1, 0, 0), angle=-vp.pi / 2)
        disc.pos = vp.vec(0, -(cone_height + base_height) / 2, 0)

        self.shape = vp.compound(
            [cone, disc], pos=vp.vec(*geo_pos), visible=False, opacity=0.6
        )

        self.update_pos(cm_pos, axis, up)
        self.shape.visible = True
