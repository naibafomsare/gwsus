r"""
======================
Rigid bodies and wires
======================

.. warning::

    Documentation under construction   
    This section is incomplete and subject to change.

The fist step is to gather the values of the physical parameters of bodies in data structures that the software understands.
This tutorial exemplifies this process for KAGRA's SR2 suspension :cite:p:`Akutsu-2021`.
The components that will be specified are the ground, two geometric anti-spring (GAS) filters, a marionette, the mirror, and the recoil masses of the latter two. Neither the inverted pendulum nor the damper ring have been implemeted yet, and are therefore not mentioned.
"""


# %%
# Import libraries
# ----------------------------

# %%
# The first library to load contains the definition of the data
# classes of the different bodies of the suspension, namely,
# mirrors, recoil masses, GAS filters, etc.
import gwsus as sus

# %%
# The next one provides the physical information of the materials
# for the wires. Currently, it includes maraging steel, high-carbon
# steel C85 for piano wires, and tungsten.
import gwsus.materials as materials

# %%
# The following library contains the definitions of the VPython 3D object
# classes used for the graphical representation of the suspension and
# animation of the resonant modes. Eventually, there will be a tutorial
# on how to implement new shapes.
from gwsus import shapes3d as shapes

# %%
# The last library provides useful functions for common tasks,
# like producing the position vectors of attachment points laid
# out at the vertices of rectangles and triangles, etc.
from gwsus import utils


# %%
# Properties of bodies
# -----------------------------------------
# For ease of use, the user is required to specify the parameter as regular Python floats.
# The initialization methods of the data classes later convert these values to Symengine rationals.

# %%
# Mirror
# ~~~~~~
# Although it is possible to use numerical values directly as parameters of data class
# constructors, for the sake of clarity, it is suggested to assign them first to a varible
# with a descriptive name. Thus, the mass of the mirror is declared first as follows:
mass = 10.170

# %%
# Next, the matrix which will become the moment of inertial is declared via one of the
# utility functions, which creates a Symengine diagonal matrix with rational elements.
# The numerical matrix elements were calculated from the 3D-CAD using Autodesk Inventor:
moi = utils.matrix_3x3_diagonal( 0.079453125,
                                 0.059152666977847504,
                                 0.059152666977847504 )

# %%
# The following is a dictionary, whose sole value is a list of the position vectors of
# the attachment points for wires, and whose sole key is the name given to them as a set: 
pos_MIR = { 'for_IM': utils.rectangle( 2*5e-3 , 2*130e-3 , 0 ) } 

# %%
# The name should be descriptive of the function of the wires. The mirror has four 
# ttachment points, which are all used to hang from the Intermediate Mass (IM).
# Therefore, the name of the set is ``'for_IM'``. The function :func:`utils.rectangle`
# generates a list of position vectors laid out in the vertices of a rectangle whose
# sides are aligned with ethe longitudinal and transverse directions. The rectangle
# is centered at the center of mass when seen from above, and displaced from it
# vertically when seen from the side. The first and second arguments are the
# **separations of the wires** in the longitudinal and transverse direction
# respectively. The third one is the vertical distance of the rectangle plane from
# the center of mass.
#
# Next comes the statement gathering the above information into the ``BodyData`` data class:
MIR = sus.BodyData( mass = mass,
                    moi = moi,
                    pos = pos_MIR,
                    shape = shapes.MirrorShape )

del  mass, moi

# %%
# The names of the first three arguments are self-explanatory.
# The last one specifies the VPython 3D object class used for
# the graphical representation of the mirror. Because some of
# the data classes only take data with keywords, it is suggested
# to do it for all of them. Deleting the values of ``mass`` and
# ``moi`` in the last line is not formally necessary, but it was
# done as a precaution to avoid leaking wrong values when these
# variable names are used again below. 


# %%
# Recoil mass
# ~~~~~~~~~~~
# The specification of the Recoil Mass (RM) is completely analogous to that of the mirror because it also hangs from the IM:
mass = 12.036
moi  = utils.matrix_3x3_diagonal( 0.2111 , 0.17165 , 0.17165 )
pos_RM = { 'for_IM': utils.rectangle( 2*10e-3 , 2*145e-3 , 0 ) } 

RM = sus.BodyData( mass = mass,
                   moi = moi,
                   pos = pos_RM,
                   shape = shapes.RecoilMassShape )

del  mass, moi

# %%
# Intermediate Mass IM
# ~~~~~~~~~~~~~~~~~~~~
# The specification of the Intermediate Mass requires additional elements because it couples to the mirror, to the IM and to the Bottom Filter (BF):
mass = 25.7 + 2 * 1.225 + 1.394
factorX = 1.9
factorY = 1.3
moi = utils.matrix_3x3_diagonal( factorY*0.1835 , factorX*0.15267 , 0.2491 )
XXX = 1.8e-3 ;

pos_IM = { 'for_BF': utils.center( -13.4e-3 ),
           'for_MIR': utils.rectangle( 2*5e-3 , 2*130e-3 , -XXX ),
           'for_RM': utils.rectangle( 2*10e-3 , 2*145e-3 , -XXX ) } 

IM = sus.BodyData( mass = mass,
                   moi = moi,
                   pos = pos_IM,
                   shape = shapes.IntermediateMassShape )
del  mass, moi

# %%
# The attachment point specifications for the mirror and RM wires ressemble those defined above because the wires are meant to be vertical. 
# The one for the Bottom Filter, ``'for_BF'``, is specified with the function :func:`utils.center`, which genetrates the position vector of a point above the center of mass by the amount indicated by its argument. 

# %%
# Intermediate Recoil Mass IRM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The attachtment points of this component are specified with the function
# :func:`utils.triangle` that produces position vectors at the vertices of an
# equilateral triangle:
mass = 8.933
moi = utils.matrix_3x3_diagonal( 0.1821 , 0.1762 , 0.29221 )
pos_IRM = { 'for_BF': utils.triangle( 2*158e-3 , 60.5e-3 , '-L') }

IRM = sus.BodyData( mass = mass,
                    moi = moi,
                    pos = pos_IRM,
                    shape = shapes.IntermediateRecoilMassShape )

del  mass, moi

# %%
# The triangle is centered at the center of mass when seen from above,
# and displaced from it vertically when seen from the side.
# The first and second arguments are the pitch circle diameter and the
# vertical distance of the triangle plane from the center of mass.
# The third argument is the direction to which the triangle points to
# if it were an arrow. It can either point to the positive (``'+L'``)
# or negative (``'-L'``) longitudinal directions.

# %%
# Bottom Filter BF
# ~~~~~~~~~~~~~~~~
# A GAS filter has three additional parameters, the resonance frequency in Hz,
# here represented by ``f0``, the saturation value of the transfer function
# and the loss angle of the spring constant:
mass = 100.21
f0 = 0.250
saturation = -1e-3
loss_angle = 1e-4

moi = utils.matrix_3x3_diagonal( 3.670091 , 3.662444 , 6.095939 )

pos_BF = { 'for_F1':utils.center( 20e-3 ),
           'for_IM' : utils.center( -12.5e-3 ),
           'for_IRM':utils.triangle( 2*158e-3 , -107e-3 , '-L') }

# %%
# To accomodate the new parameters, a different data class is used now: 
BF = sus.GASFilterData( mass = mass,
                        moi = moi,
                        pos = pos_BF,
                        resonance_frequency = f0,
                        saturation = saturation,
                        loss_angle = loss_angle,
                        shape = shapes.GASFilterShape )

del  mass, f0, saturation, loss_angle, moi


# %%
# Standard Filter F1
# ~~~~~~~~~~~~~~~~~~
# The specification of the Standard Filter F1 is analogous to that of
# the BF, with the difference of not having a diagonal moment of inertia,
# which is defined with a different utility function:

mass = 91.31
f0 = 0.250
saturation = -1e-3
loss_angle = 1e-4

moi = utils.matrix_3x3( [ [ 3.8399, 0.61  , 0      ],
                          [ 0.61  , 3.8399, 0      ],
                          [ 0     , 0     , 6.4676 ] ] )

pos_F1 = { 'for_GND':utils.center( -13.5e-3 ),
           'for_BF' : utils.center( -24.6e-3 ) }

F1 = sus.GASFilterData( mass = mass,
                        moi = moi,
                        pos = pos_F1,
                        resonance_frequency = f0,
                        saturation = saturation,
                        loss_angle = loss_angle,
                        shape = shapes.GASFilterShape ) 

del  mass , f0 , saturation , loss_angle , moi

# %%
# As suggested by the name of the first attachment point, this GAS filter hangs directly from the ground.
#
# Ground GND
# ~~~~~~~~~~
# The ground defines the origin of the suspension reference frame,
# and it is the simplest component as it only has one attachment point:
pos_GND = { 'for_F1' : utils.center(0) }
GND = sus.GroundData( pos = pos_GND )


# %%
# Properties of wires
# ----------------------------------------
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

# %%
# For mirror
# ~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 4
material = materials.piano_wire
diameter =  0.2e-3 
length =  587e-3 

wire_MIR = sus.WireData( number = number,
                         material = material,
                         diameter = diameter,
                         length = length )

del number, material, diameter, length

# %%
# For Recoil Mass
# ~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 4
material = materials.tungsten
diameter =  0.6e-3 
length =  587e-3

wire_RM = sus.WireData( number = number,
                        material = material,
                        diameter = diameter,
                        length = length )

del number , material , diameter , length

# %%
# For Intermediate Mass
# ~~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = ( 2e-3 , 2.5e-3 , 2e-3 )
length = ( 26.5e-3 , 545.5e-3 , 26.5e-3 ) 

wire_IM = sus.WireData( number = number,
                        material = material,
                        diameter = diameter,
                        length = length )

# %%
# For Intermediate Recoil Mass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 3
material = materials.maraging_steel
diameter = 2.0e-3 
length = 355.0e-3

wire_IRM = sus.WireData( number = number,
                         material = material,
                         diameter = diameter,
                         length = length )

# %%
# For Bottom Filter
# ~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = ( 2.5e-3 , 4.5e-3 , 2.5e-3 )
length = ( 26.5e-3 , 513.4e-3 , 26.5e-3 )

wire_BF = sus.WireData( number = number,
                        material = material,
                        diameter = diameter,
                        length = length )


# %%
# For Standard Filter
# ~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = ( 3e-3 , 4.5e-3 , 3e-3 )
length = ( 26.5e-3 , 1280e-3 , 26.5e-3 )

wire_F1 = sus.WireData( number = number,
                        material = material,
                        diameter = diameter,
                        length = length )


