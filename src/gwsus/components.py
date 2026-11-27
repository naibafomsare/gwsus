import symengine as se
import numpy as np  # for element-wise operations on wires with necks
import bigtree as bt
from . import dataclasses
from . import utils
from . import shapes3d
from .info import vprint


class Ground(bt.Node):
    """
    This component represents the ground onto which the mechanical
    system is placed. Its position defines the origin of the suspension
    reference frame.
    """

    # To generate the symbolic variables for the body coordinates.
    _names = ["lon", "tra", "ver", "roll", "pitch", "yaw"]

    def __init__(self, name, data, **kwargs):
        """
        Initialize the instance.

        Parameters
        ----------
        name : str
            Abbreviated name of the ground component, typically ``GND``.
        data : gwsus.utils.GroundData
            Data class with the attachment point displacement vectors.
        """

        # Call bigtree node constructor
        super().__init__(name=name, **kwargs)

        self.name = name

        # w.r.t. the center of mass
        self.attachment_points_p = data.pos
        """
        Dictionary with the displacement vectors of the attachment points,
        grouped by function and expressed w.r.t. the local reference frame
        at the suspension origin in the case of the ground, or at the center
        of mass in the case of children classes.
        
        * Key: name of the attachment point set, e.g., ``'for_IRM'``, ``'for_MIR'``,
          ``'for_F1'``, etc.
        
        * Value: list of column vectors, with the number of vectors depending on the
          number of attachment points needed, e.g., for the mirror four are needed
          whereas for a GAS filter only one.
        
        * Provided by the parameter **data**.
        
        * For internal use but accesible for user inspection.
        """

        self.load = 0  # Check whether utils.con(0) or None are better

        # Declare displacement symbolic variables
        s = " ".join([item + self.name for item in Ground._names])
        self.lon, self.tra, self.ver, self.roll, self.pitch, self.yaw = se.symbols(
            s, real=True
        )

        self.r = se.Matrix([self.lon, self.tra, self.ver])
        """Column vector with the symbolic coordinates of the center of mass."""

        self.angles = se.Matrix([self.roll, self.pitch, self.yaw])
        """Column vector with the symbolic angles of the body orientation."""

        self.attachment_points_r: dict[str, list[se.Matrix]] = {}
        """
        Dictionary with the displacement vectors of the attachment points
        expressed w.r.t. the suspension reference frame defined by the ground.
        
        * Key: name of the attachment point set, e.g., ``'for_IRM'``, ``'for_MIR'``,
          ``'for_F1'``, etc.
        * Value: list of column vectors, with the number of vectors depending on the
          number of attachment points needed, e.g., for the mirror four are needed
          whereas for a GAS filter only one.
        * For internal use but accesible for user inspection.
        """
        # -- start-logic-tag --
        # A key is the name of an attachment point set
        # A value is a list of position vectors
        for key, value in self.attachment_points_p.items():
            self.attachment_points_r[key] = [
                self.r + utils.rotB2S(self) * vector_p for vector_p in value
            ]
        # -- end-logic-tag --

        self.body_coords = []
        self.float_coords = []
        self.gnd_coords = self.r.T.tolist()[0] + self.angles.T.tolist()[0]

    def update(self):
        """Calculate the load that the component supports."""
        if not self.is_leaf:
            self.load = sum((child.load + child.mass) for child in self.children)


class RigidBody(Ground):
    """
    This class is for representing bodies without internal springs, e.g.,
    mirrors, intermediate masses, recoil masses, etc.
    """

    def __init__(self, name, data, **kwargs):
        """
        Initialize the instance.

        Parameters
        ----------
        name : str
            Abbreviated name of the rigid body, e.g., ``MIR``, ``RM``,
            ``IM``, ``IRM``, etc.
        data : gwsus.utils.BodyData
            Data class with physical specification of the rigid body,
            including coordinates of attachment points w.r.t. the center of mass.
        """

        Ground.__init__(self, name, data, **kwargs)

        self.mass: se.Rational = data.mass
        """Body mass"""

        self.moi: se.Matrix = data.moi
        """Moment of inertia"""

        self.link: gwsus.components.Wire = None
        """Link instance the body couples with to its parent node"""

        # List with internal link instances.
        # It's only used for GAS filters and IPs,
        # and for a rigid body it remains empty.
        # Is it necessary to declare it in the Body class?
        self.link_internal = []

        # Velocity symbolic variables
        s = " ".join(["v" + item + self.name for item in RigidBody._names])
        self.vlon, self.vtra, self.vver, self.vroll, self.vpitch, self.vyaw = (
            se.symbols(s, real=True)
        )

        self.v = se.Matrix([self.vlon, self.vtra, self.vver])
        """Column vector with the symbolic velocities w.r.t. the suspension reference frame."""

        vangles = se.Matrix([self.vroll, self.vpitch, self.vyaw])
        """Column vector with the symbolic velocities in roll, pitch and yaw."""

        # -- start-logic-tag-angular-velocity --
        self.omega = (
            se.Matrix(
                [
                    [1, 0, -se.sin(self.pitch)],
                    [0, se.cos(self.roll), se.sin(self.roll) * se.cos(self.pitch)],
                    [0, -se.sin(self.roll), se.cos(self.roll) * se.cos(self.pitch)],
                ]
            )
            * vangles
        )
        # -- end-logic-tag-angular-velocity --
        """Angular velocity column vector, expressed w.r.t. the suspension
        reference frame and in terms of roll, pitch and yaw symbolic variables."""

        # Override the assignment from parent class ``Ground``
        self.body_coords = self.gnd_coords
        self.gnd_coords = []

        self.grav_Ep: se.Basic = self.mass * utils.g * self.ver
        """Gravitational potential energy"""

        self.Ek: se.Basic = se.Rational(1, 2) * (
            self.mass * self.v.dot(self.v) + self.omega.T.dot(self.moi * self.omega)
        )
        """Kinetic energy"""

        self.shape: type[gwsus.shapes3d.BasicBodyShape] = data.shape
        """Equals to the definition of the VPython 3D object class, not to
        an instance of the class."""

        self.shape_instance: gwsus.shapes3d.BasicBodyShape = None
        """Equals to the instance of the VPython 3D object class."""

        # Orientation of the body and its links for animation
        self.orien_lambda = None
        self.orienw_lambda = None

    def update(self):
        """
        Calculate the load of the body and the load of the link or
        links the body hangs from.
        """
        super().update()

        # Calculate the load of the link the body hangs from
        link = self.link
        link.load = self.mass + self.load

        # Load of individual links of the set of links
        link.load_single = link.load / link.num

        # Tension in individual links of the set
        link.tension = link.load_single * utils.g
        self.link.update()


# --------------- Links --------------------#


class Spring:
    """
    Implementation of springs.

    An instance represents a set of springs, where there can be
    only one spring. It is the parent class for ``Wire``, whose
    instances typically have one, three or four wires. Springs
    and wires are generically called *links*.

    * **Check whether it is directly usable or only a parent class for ``Wire``.**
    """

    def __init__(self, data):
        """
        Initialize the instance.

        Parameters
        ----------
        data : gwsus.utils.SpringData
            Data class with the physical specification of the spring.
        """
        self.shape = None
        self.damp_factor: symengine.lib.symengine_wrapper.Complex = (
            1 + se.I * data.loss_angle
        )
        """Complex factor that mutiplies the real-value spring constant and introduces
        structural damping."""

        self.num: int = data.number
        """Number of individual links in the set"""

        self.k_axial: symengine.lib.symengine_wrapper.Mul = data.k_axial
        """Spring constant along the length of an individual link"""

        self.k_torsion: symengine.lib.symengine_wrapper.Mul = data.k_torsion
        """Torsional spring constant of an individual link"""

        self.length: symengine.lib.symengine_wrapper.Rational = data.length
        """Unstretched length"""

        self.shape: gwsus.shapes3d.SpringShape = shapes3d.SpringShape
        """Equals to the definition of the VPython 3D object class, not to an instance
        of the class."""

        # Load of the set of springs.
        # In `Spring` and `Wire` used only for printing information on the screen.
        self.load = None
        self.load_single = None  # Load of the individual springs. In `Spring` and `Wire` used only for printing information on the screen.
        self.tension = None  # Tension in individual springs

        # To be updated by method `calculate_stretched_length` in this class.
        # Total stretched length of wire.
        self.l_stretch: symengine.lib.symengine_wrapper.Add = utils.con(0)

        # Vertical length of the link in equilibrium.
        # Used only to guess the vertical equilibrium
        # positions of the bodies in method `supension.guess_equi_coords`.
        # It must either be given or calculated in a method.
        # In class `Wire`, in method `calculate_stretched_length`,
        # it's set equal to the stretched length assuming
        # the wire is vertical in equilibrium. When it's not
        # vertical an angle is needed, but this hasn't been implemented yet.
        # Default value:
        self.vlength: symengine.lib.symengine_wrapper.Add = utils.con(0)
        """Vertical length of the link in equilibrium. Used only to guess the vertical
        equilibrium positions of the bodies in method ``supension.guess_equi_coords()``."""

        # ----- To be updated by `suspension.connect` method --------#

        self.r_upper: list = []
        """List with position vectors of the upper attachment points. Also in the upper
        body's dictionary ``attachment_points_r``, but gathered here for ease of access.
        Updated in method ``suspension.connect()``."""

        self.r_lower: list = []
        """List with position vectors of the lower attachment points. Also in the lower
        body's dictionary ``attachment_points_r``, but gathered here for ease of access.
        Updated in method ``suspension.connect()``."""

        self.angles_lower = None
        self.angles_upper = None
        # self.body = None # Write here why we need this.

        # For calculating the axial and torsional potential energies,
        # and for the animation. To be updated in method `calculate_geometry`
        self.r_diff: list = []
        """List with vectors ``self.r_upper - self.r_lower``, i.e., vectors point upwards."""

        self.norm_diff: list = []
        """List with the norms of the elements of ``self.r_diff``."""

        # Elastic potential energy dictionary
        self.Ep_dict = {
            "axial": {"damp": self.damp_factor, "energy": utils.con(0), "master": None},
            "torsion": {
                "damp": self.damp_factor,
                "energy": utils.con(0),
                "master": None,
            },
            "bend": {"damp": utils.con(0), "energy": utils.con(0), "master": None},
        }

    def update(self):
        """
        Call the methods ``calculate_stretched_length()`` and ``calculate_geometry()``
        in this order.
        """
        # `calculate.stretched_length` is only useful in this class for
        # guessing equilibrium values. In derived class ``Wire`` it is overriden.
        self.calculate_stretched_length()
        self.calculate_geometry()

    def calculate_stretched_length(self):
        """
        Calculate the stretched length of the links under its load.
        """
        # L0 and k are scalars because springs don't have necks.
        # In class ``Wire`` they are numpy arrays because suspension rods can have necks.
        T = self.tension  # Tension in the individual wire
        L0 = self.length  # Unstretched original length
        k = self.k_axial
        self.l_stretch = L0 + T / k
        self.vlength = self.l_stretch  # Estimate of the vertical length in equilibrium.
        # print( 'vlength spring:' , float(self.vlength) ) #######################################

    def calculate_geometry(self):
        """
        Calculate the vector differences between attachment points and their norms.

        This information is required to calculate the axial and torsional potential energies,
        and for the animation of the wires. It can be called after ``suspension.connect()``
        and, in the current implementation, it is called in ``suspension.update()`` via ``link.update()``.
        """
        for index in range(self.num):

            # This vector points upwards
            r_diff = self.r_upper[index] - self.r_lower[index]
            norm_diff = se.sqrt(r_diff.dot(r_diff))

            self.r_diff.append(r_diff)
            self.norm_diff.append(norm_diff)

    # Currently not in use
    def calculate_bending_Ep(self):
        """
        Calculate the bending potential energy. This funtion has not been implemented yet.
        """
        return utils.con(0)  # Symbolic zero

    # Method currently used for derived classes `Wire` and `Spring`.
    # For classes that don't require it, override it with:
    #
    # def calculate_axial_Ep( self ):
    #     return utils.con(0) # Symbolic zero
    #
    def calculate_axial_Ep(self):
        """
        Calculate elastic potential energy along the length of the link.

        It returns the result and also saves it in ``self.Ep_dict['axial']['energy']``

        Returns
        -------
        symengine.lib.symengine_wrapper.Mul
            Algebraic expression of the axial potential energy.
        """
        add = 0
        for index in range(self.num):
            # In the code below, np.sum( self.length ) is the sum of the wire segments without load.
            # It still works even when self.length is a float or a tuple.
            add = add + (self.norm_diff[index] - np.sum(self.length)) ** 2
        total = se.Rational(1, 2) * self.k_axial * add
        self.Ep_dict["axial"]["energy"] = total
        return total

    # Maybe this note ca be removed. I'm not sure it's useful.
    # Method currently used for derived classes `Wire` and `Spring`.
    # For classes that don't require it, override it with:
    #
    # def calculate_torsion_Ep( self ):
    #     return utils.con(0) # Symbolic zero
    #
    def calculate_torsion_Ep(self):
        """
        Calculate the torsional elastic potential energy.

        It requires knowledge of the equlibrium positions. It returns the result
        and also saves it in ``self.Ep_dict['torsion']['energy']``

        Returns
        -------
        symengine.lib.symengine_wrapper.Mul
            Algebraic expression of the torsional potential energy.
        """
        add = 0
        
        angles_diff = self.angles_upper - self.angles_lower
        
        for index in range(self.num):
            
            # Unit vector along the wire, pointing upwards in
            # equilibrium in KAGRA-style suspension.
            n = (self.r_diff[index] / self.norm_diff[index]).subs(
                self.sus.equi_coords_dict
            )
            
            add = add + angles_diff.dot(n) ** 2
            
        total = se.Rational(1, 2) * self.k_torsion * add
        
        self.Ep_dict["torsion"]["energy"] = total
        
        vprint(
            f"it dependens on {self.Ep_dict['torsion']['energy'].free_symbols}. ",
            level=2,
        )
        
        return total

    def shape_parameters(self):
        """
        Generate a dictionary with parameter values for the animation.

        To be tailored to the specific VPython 3D object class of the derived class.
        It returns a dictionary to be passed as ``**kwargs`` to method ``anime.show_anime()``.
        Currently not un used.

        Returns
        -------
        dict
            Dictionary with parameters for the animation
        """
        param = {}
        # This is a vpython vector, whose elements can
        # only be accessed with dot notation.
        # dim = self.body.shape_instance.shape.size

        param["min_dim"] = 25e-3

        # Minimum dimension in L and T of the box surrounding
        # the object that hangs from the spring.
        # min( dim.x , dim.y )
        return param


class Wire(Spring):
    """
    Currently only wires with circular cross sections are supported
    """

    def __init__(self, data):
        """
        Initialize the instance.

        Parameters
        ----------
        data : gwsus.utils.WireData
            Data class with the physical specification of the wire.
        """
        Spring.__init__(self, data)
        
        # Override the default value of 1 set in parent class
        self.num = data.number
        
        self.material: str = data.material

        # In the case of receiving a scalar,
        # `np.atleast_1d` makes the array 1D so it's subscriptable.
        self.ll: np.array = np.atleast_1d(np.array(data.length, dtype=object))
        """Segment lengths unstretched"""

        self.dd: np.array = np.atleast_1d(np.array(data.diameter, dtype=object))
        """Segment diameters"""

        self.ll_stretch = np.array([])
        """Numpy array with the stretched lengths of the link segments (for wires with necks)."""

        # Elementwise operations using numpy arrays
        # Segment's cross section areas
        self.AA = se.pi * self.dd**2 * se.Rational(1, 4)

        # Segment's 2nd moments of area
        self.JJ = se.pi * self.dd**4 * se.Rational(1, 64)

        # Segment's torsional constants
        self.JJee = se.pi * self.dd**4 * se.Rational(1, 32)

        # To be updated by `calculate_torsion_stiffness` in this class.
        # Numpy array with the torsional spring constants of the wire segments.
        self.kk_torsion: np.array = np.array([])

        self.shape = shapes3d.WireShape

    # -------- update method --------------#

    def update(self):
        """ """
        self.calculate_axial_stiffness()
        
        # For estimating equilibrium values and torsional stiffness
        self.calculate_stretched_length()
        
        self.calculate_geometry()
        self.calculate_torsion_stiffness()

    # --------- Methods to be called by the wire's `update` method --------------#

    def calculate_axial_stiffness(self):
        """ """
        E = self.material.young_modulus
        A = self.AA  # Segment cross section areas
        L0 = self.ll  # Segment lengths
        self.kk_axial = E * A / L0  # Elementwise operations using numpy arrays
        self.k_axial = utils.kk_series(self.kk_axial)  # Springs added in series

    def calculate_stretched_length(self):
        """
        Calculate the stretched length of the wire and, for wires with necks, of its segments too.

        The individual lengths of segments are required for calculating the torsional stiffness.
        """
        T = self.tension  # Tension in the individual wire
        L0 = self.ll  # Unstretched original lengths of segments
        k = self.kk_axial

        # Element-wise operations using numpy arrays
        self.ll_stretch = T / k
        
        #### print( np.sum( self.ll_stretch ).n(10) ) ###########################################

        # Sum of the stretched segments
        self.l_stretch = np.sum(L0) + np.sum(self.ll_stretch)

        # Estimate of the vertical length in equilibrium.
        # In case the link is not supposed to be vertical,
        # its projection on the vertical should be given here.
        self.vlength = self.l_stretch

    def calculate_torsion_stiffness(self):
        """ """
        # self.calculate_stretched_length()
        G = self.material.shear_modulus
        Je = self.JJee  # Segment torsional constants
        T = self.tension  # Tension in the individual wire
        J = self.JJ  # Segment 2nd moment of area
        A = self.AA  # Segment cross section areas
        L = self.ll_stretch

        # Element wise operations using numpy arrays
        self.kk_torsion = (G * Je + T * J / A) / L

        # Springs added in series
        self.k_torsion = utils.kk_series(self.kk_torsion)


# ------------ Flexible bodies ----------------#


class InternalSprings:

    def __init__(self):

        # Create the spring instances
        ########## Why is the loss angle set to 1e-4 here?
        spring_data = dataclasses.SpringData(
            number=1, k_axial=None, length=utils.con(0), loss_angle=utils.con(1e-4)
        )
        
        self.springs = [Spring(data=spring_data) for _ in range(self.num)]

        # Rotation matrix
        rot = utils.rotB2S(self)

        # Connect the springs and add them to the list link.internal
        for idx, link in enumerate(self.springs):

            # Position of spring in global coordinates,
            # deepcopy does not work on symengine matrices.
            spr_r_copy = se.Matrix(self.spr_r[idx].tolist())

            link.r_upper = [spr_r_copy]

            # self.dir_p is in local coordinates.
            link.r_lower = [spr_r_copy + rot * self.dir_p[idx]]

            self.link_internal.append(link)

        # Cross product with the body's angular velocity.
        # This matrix is already in RigidBody, adapt so
        # it's not written again here!
        omegax = se.Matrix(
            [
                [utils.con(0), -self.omega[2], self.omega[1]],
                [self.omega[2], utils.con(0), -self.omega[0]],
                [-self.omega[1], self.omega[0], utils.con(0)],
            ]
        )

        # Velocity of the point masses that represent
        # the masses of the massive springs
        half = se.Rational(1, 2)
        self.ratio = ratio = utils.con(1 / 2)

        self.v1 = [
            self.v + omegax * rot * half * vec_p + rot * half * vec_vp
            for vec_p, vec_vp in zip(self.dir_p, self.dir_vp)
        ]

        self.v2 = [
            self.v - omegax * rot * ratio * vec_p - rot * ratio * vec_vp
            for vec_p, vec_vp in zip(self.dir_p, self.dir_vp)
        ]

    def update(self):

        # For a GASFilter num=1, for an IP num=3, for a PreIsolator num=4.
        M = self.spring_load / self.num
        ratio = self.ratio  # Cannot be zero

        for link, f0, beta, v1, v2 in zip(
            self.springs, self.f0, self.beta, self.v1, self.v2
        ):
            m1 = utils.con(0.1)

            # in terms of ( M , beta , m1 , ratio ) # Check whether m2 > 0!!!!!!!!!!!!!!!!
            m2 = (-4 * M * beta - beta * m1 + m1) / (
                4 * ratio * (beta * ratio + ratio + 1)
            )

            self.Ek = (
                self.Ek
                + se.Rational(1, 2) * m1 * v1.dot(v1)
                + se.Rational(1, 2) * m2 * v2.dot(v2)
            )

            # link.k_axial = ( 2 * se.pi * f0 )**2 * ( M + m1/4 + m2*ratio**2 ) # in terms of ( f0 , M , m1 , m2 , ratio )
            # in terms of ( f0 , M , m1 , m2 , ratio )
            link.k_axial = (2 * se.pi * f0) ** 2 * (
                M + m1 * se.Rational(1, 4) + m2 * ratio**2
            )
            
            vprint(
                f"{self.name}: beta, m1, m2 = {beta.evalf()} , {m1.evalf()} , {m2.evalf()}",
                level=1,
            )
            
            link.update()
            
            # This makes the length of the spring zero
            link.length = link.l_stretch

            # print( link.length.n(10) )


class GASFilter(RigidBody, InternalSprings):

    def __init__(self, name, data, **kwargs):

        RigidBody.__init__(self, name, data, **kwargs)

        # self.f0 and self.beta must be in a list, even
        # if they have only one element.
        # It's a requirement for class InternalSprings
        d1 = data.resonance_frequency

        # if d1 not a list or tuple take the value and put it in a list,
        # otherwise keep it as a list or tuple.
        self.f0 = [d1] if type(d1) not in (list, tuple) else d1
        d2 = data.saturation
        self.beta = [d2] if type(d2) not in (list, tuple) else d2

        # The body the internal springs holds, i.e., the load of the GAS filter.
        # To be updated ``suspension.connect``, used to calculate the spring
        # load in method `update()` below.
        self.spring_body = None

        # Scalar displacement quantifying the spring
        # deformation in local coordinates
        self.q = se.symbols("q" + self.name, real=True)

        # Velocity, used in Ek when the spring has mass
        self.vq = se.symbols("vq" + self.name, real=True)

        # Unit vector along which the motion is constrained,
        # in local coordinates
        self.direction = se.Matrix([0, 0, 1])

        # Add parameter self.q to the list of body coordinates,
        # the spring and the counterweight always have mass.
        self.body_coords.append(self.q)

        # if self.beta[0] == utils.con( 0 ): # A GAS filter has only one spring
        #     print( f"{self.name}: massless spring with float coordinate q{self.name}, " , end="")
        #     self.float_coords.append( self.q ) # Parameter added to the list of float coordinates
        # else:
        #     print( f"{self.name}: spring with mass, " , end="")
        #     self.body_coords.append( self.q ) # Parameter added to the list of body coordinates

        self.name_for_spring = self.attach_point_center_down()

        # For the attachment points of the spring, used in InternalSprings.__init__( self )

        self.num = 1  # Only one spring

        # List with the position vector of the spring, in global coordinates.
        self.spr_r = self.attachment_points_r[self.name_for_spring]

        # List with direction vectors of the springs, in local coordinates.
        self.dir_p = [self.direction * self.q]

        # List with velocity vectors of the springs, in local coordinates.
        self.dir_vp = [self.direction * self.vq]

        # Initialize internal springs
        InternalSprings.__init__(self)

        # Update the lower attachment point with the modifications from InternalSprings
        # self.springs only has one element in the GAS filter
        self.attachment_points_r[self.name_for_spring] = self.springs[0].r_lower

    def attach_point_center_down(self):
        # In class `GASFilter` return the one which is physically below.

        # From the two atachment points at the center
        # extract the name of the points for which x=y=0.
        name_center = [
            name
            for (name, coords) in self.attachment_points_p.items()
            if (coords[0][0] == coords[0][1] == 0)
        ]

        # Identity the lower one from those two
        p0 = self.attachment_points_p[name_center[0]]
        p1 = self.attachment_points_p[name_center[1]]
        if p0[0][2] < p1[0][2]:
            point_name = name_center[0]
        else:
            point_name = name_center[1]

        vprint(
            f"{self.name}: the spring attachment point " f"is called '{ point_name }'.",
            level=1,
        )

        return point_name

    def update(self):

        # Update per the parent class RigidBody, which updates the external link.
        RigidBody.update(self)

        # This is in the child class because tension=0 must be set for an IP but not for the GAS Filter.
        # However, tension=0 might work for both if the stretched length of the springs is set to a
        # constant value independent of the tension, as this calss is implemented from the begining.
        self.spring_load = self.spring_body.mass + self.spring_body.load
        for link in self.springs:
            # For an IP this tension must be set to zero
            link.tension = self.spring_load * utils.g / self.num

        InternalSprings.update(self)

        # print( self.link.Ep_dict['torsion'] ) ######################################################
