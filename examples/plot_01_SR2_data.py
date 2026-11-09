"""
======================
Rigid bodies and wires
======================

.. warning::

    Documentation under construction   
    This section is incomplete and subject to change.

The fist step is to gater the values of the physical parameters of bodies in a data structure that the software understands.
This example shows how to accomplish this for KAGRA's SR2 suspension [citation].

The components that will be specified are the ground, two geometric anti-spring (GAS) filters, a marionette, the mirror, and the recoil masses of the latter two. Neither the inverted pendulum nor the damper ring have been implemeted, and are therefore not described yet.
"""


# %%
# Import libraries
# ----------------------------

# %%
# In this particular example, the first library to load is Symengine, which provides high-speed symbolic calculations. In a future update this library will not be loaded directly in this example and this line will be removed.
import symengine as se

# %%
# The next library contains the definition of the data classes of the different bodies of the suspension, namely, mirrors, recoil masses, GAS filters, etc.
import gwsus as sus

# %%
# The next library provides the physical information of the materials for the wires. Currently, it includes maraging steel, high-carbon steel C85 for piano wires, and tungsten.
import gwsus.materials as materials

# %%
# The following library contains the definitions of the VPython 3D oblect classes used for graphical representation and animation of the resonant modes. Evententually, there wil be a tutorial on how to implement new shapes. 
from gwsus import shapes3d as shapes

# %%
# The last library provides useful functions for common tasks, like producing the position vectors of attachment points laid out as the vertices of rectangles and triangles, etc.
from gwsus import utils


# %%
# Physical properties of bodies
# -----------------------------------------
# The next step is to specify the physical properties of the bodies.

# %%
# Mirror
# ~~~~~~
# The ``mass`` parameter is specified with a single ``float``. The second parameter is the moment of inertial ``moi``, which is specified with a function that creates a Symengine diagonal matrix with rational numeric elements. In this example, the moment of inertia was calculated from the 3D-CAD in Autodesk Inventor.
mass = 10.170
moi = utils.moi_diagonal( 0.079453125 , 0.059152666977847504 , 0.059152666977847504 )

# %%
# The following parameter is a dictionary that gives names to sets of position vectors of attachment points: 
pos_MIR = { 'for_IM' : utils.rectangle( 2*5e-3 , 2*130e-3 , 0 ) } 
# %%
# In the case of the mirror, its four the attachment points are for coupling it with the marionette above, and therefore, they are all grouped under the name ``'for_IM'``. The function :func:`utils.rectangle` generates a list of laid out in the vertices of a rectangle.

MIR = sus.BodyData( mass = mass,
                    moi = moi,
                    pos = pos_MIR,
                    shape = shapes.MirrorShape )

del  mass, moi

# %%
# Recoil mass
# ~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 12.036
moi  = utils.moi_diagonal( 0.2111 , 0.17165 , 0.17165 )
pos_RM = { 'for_IM' : utils.rectangle( 2*10e-3 , 2*145e-3 , 0 ) } 

RM = sus.BodyData( mass = mass,
                   moi = moi,
                   pos = pos_RM,
                   shape = shapes.RecoilMassShape )

del  mass, moi

# %%
# Intermediate Mass IM
# ~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 25.7 + 2 * 1.225 + 1.394
factorX = 1.9
factorY = 1.3
moi = utils.moi_diagonal( factorY*0.1835 , factorX*0.15267 , 0.2491 )
XXX = 1.8e-3 ;

pos_IM = { 'for_BF':utils.center( -13.4e-3 ),
           'for_MIR' : utils.rectangle( 2*5e-3 , 2*130e-3 , -XXX ),
           'for_RM' : utils.rectangle( 2*10e-3 , 2*145e-3 , -XXX ) } 

IM = sus.BodyData( mass = mass,
                   moi = moi,
                   pos = pos_IM,
                   shape = shapes.IntermediateMassShape )
del  mass, moi

# %%
# Intermediate Recoil Mass IRM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 8.933
moi = utils.moi_diagonal( 0.1821 , 0.1762 , 0.29221 )
pos_IRM = { 'for_BF': utils.triangle( 2*158e-3 , 60.5e-3 , '-L') }

IRM = sus.BodyData( mass = mass,
                    moi = moi,
                    pos = pos_IRM,
                    shape = shapes.IntermediateRecoilMassShape )

del  mass, moi

# %%
# Bottom Filter BF
# ~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.
mass = 100.21
f0 = 0.250
saturation = -1e-3
loss_angle = 1e-4

moi = utils.moi_diagonal( 3.670091 , 3.662444 , 6.095939 )

pos_BF = { 'for_F1':utils.center( 20e-3 ),
           'for_IM' : utils.center( -12.5e-3 ),
           'for_IRM':utils.triangle( 2*158e-3 , -107e-3 , '-L') }

BF = sus.GASFilterData( mass = mass,
                        moi = moi,
                        pos = pos_BF,
                        resonant_frequency = f0,
                        saturation = saturation,
                        loss_angle = loss_angle,
                        shape = shapes.GASFilterShape )

del  mass, f0, saturation, loss_angle, moi


# %%
# Standard Filter F1
# ~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 91.31
f0 = 0.250
saturation = -1e-3
loss_angle = 1e-4

moi = se.Matrix(  [ [ *utils.con( 3.8399 , 0.61 , 0 ) ],
                    [ *utils.con( 0.61 , 3.8399 , 0 ) ],
                    [ *utils.con( 0 , 0 , 6.4676 ) ] ] )

pos_F1 = { 'for_GND':utils.center( -13.5e-3 ),
           'for_BF' : utils.center( -24.6e-3 ) }

F1 = sus.GASFilterData( mass = mass,
                        moi = moi,
                        pos = pos_F1,
                        resonant_frequency = f0,
                        saturation = saturation,
                        loss_angle = loss_angle,
                        shape = shapes.GASFilterShape ) 

del  mass , f0 , saturation , loss_angle , moi

# %%
# Ground GND
# ~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

pos_GND = { 'for_F1' : utils.center(0) }

# pos_GND = { 'for_BF' : utils.center(0) }
# pos_GND = { 'for_IM' : utils.center(71e-3), 'for_IRM' : utils.triangle( 2*158e-3 , -23.5e-3 , '-L') }

GND = sus.GroundData( pos = pos_GND )

# %%
# Physical properties of wires
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
length =  utils.con(587e-3) 

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
length =  utils.con(587e-3)

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
length = utils.con( 26.5e-3 + 545.5e-3 + 26.5e-3 ) # Should be changed to separation with commas
# length = utils.con( 26.5e-3 , 545.5e-3 , 26.5e-3 ) # Should be changed to separation with commas
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
length = utils.con( 355.0e-3 )

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
length = utils.con( 26.5e-3 + 513.4e-3 + 26.5e-3 ) # Should be changed to separation with commas

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
length = utils.con( 26.5e-3 + 1280e-3 + 26.5e-3 )

wire_F1 = sus.WireData( number = number,
                        material = material,
                        diameter = diameter,
                        length = length )


