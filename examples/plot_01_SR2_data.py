"""
======================
Rigid bodies and wires
======================

.. container:: construction-notice

    **🛠️⛏️ Documentation under construction**   
    This section is incomplete and subject to change.

This example shows how to define the individual components of SR2 suspension. These are the ground, the GAS filters, the mirror, the intermediate mass and the recoil masses of the latter two. Once implemented, the inverted pendulum and the damper ring will explained here too.

* Uses International System units
"""


# %%
# Import libraries
# ----------------------------
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.
#
# * The Symengine library will be removed from this example once a better implementation of the F1 moment of inertia matrix is written.
# * 

import symengine as se
import gwsus.materials as materials
from gwsus import utils
from gwsus import shapes3d as shapes

# %%
# Specify the physical properties of bodies
# ----------------------------
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

# %%
# Mirror
# ~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 10.170
moi = utils.moi_diagonal( 0.079453125 , 0.059152666977847504 , 0.059152666977847504 )
pos_MIR = { 'for_IM' : utils.rectangle( 2*5e-3 , 2*130e-3 , 0 ) } 
MIR = utils.BodyData( mass = mass , moi = moi , pos = pos_MIR , shape = shapes.MirrorShape )
del  mass , moi

# %%
# Recoil mass
# ~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 12.036
moi  = utils.moi_diagonal( 0.2111 , 0.17165 , 0.17165 )
pos_RM = { 'for_IM' : utils.rectangle( 2*10e-3 , 2*145e-3 , 0 ) } 
RM = utils.BodyData( mass = mass , moi = moi , pos = pos_RM , shape = shapes.RecoilMassShape )
del  mass , moi

# %%
# Intermediate Mass IM
# ~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 25.7 + 2 * 1.225 + 1.394
factorX = 1.9 ; # Added by Fabian in order to get resonance frequency SUMCOM #35 correct. The actual MoI should be calculated from the 3D CAD.
factorY = 1.3 ;
moi = utils.moi_diagonal( factorY*0.1835 , factorX*0.15267 , 0.2491 )
XXX = 1.8e-3 ;
# pos_IM = { 'for_GND':utils.center( -13.4e-3 ) , 'for_MIR' : utils.rectangle( 2*5e-3 , 2*130e-3 , -XXX ) , 'for_RM' : utils.rectangle( 2*10e-3 , 2*145e-3 , -XXX ) } 
pos_IM = { 'for_BF':utils.center( -13.4e-3 ) , 'for_MIR' : utils.rectangle( 2*5e-3 , 2*130e-3 , -XXX ) , 'for_RM' : utils.rectangle( 2*10e-3 , 2*145e-3 , -XXX ) } 
IM = utils.BodyData( mass = mass , moi = moi , pos = pos_IM , shape = shapes.IntermediateMassShape )
del  mass , moi

# %%
# Intermediate Recoil Mass IRM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 8.933
moi = utils.moi_diagonal( 0.1821 , 0.1762 , 0.29221 )
pos_IRM = { 'for_BF': utils.triangle( 2*158e-3 , 60.5e-3 , '-L') }
# pos_IRM = { 'for_GND': utils.triangle( 2*158e-3 , 60.5e-3 , '-L') }
IRM = utils.BodyData( mass = mass , moi = moi , pos = pos_IRM , shape = shapes.IntermediateRecoilMassShape )
del  mass , moi

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
# pos_BF = { 'for_F1':utils.center( 2.5e-3 ) , 'for_IM' : utils.center( -12.5e-3 ) , 'for_IRM':utils.triangle( 2*158e-3 , -87.1e-3 , '-L') }
pos_BF = { 'for_F1':utils.center( 20e-3 ) , 'for_IM' : utils.center( -12.5e-3 ) , 'for_IRM':utils.triangle( 2*158e-3 , -107e-3 , '-L') }
BF = utils.GASFilterData( mass = mass , moi = moi , pos = pos_BF , resonant_frequency = f0 , saturation = saturation  , loss_angle = loss_angle , shape = shapes.GASFilterShape ) 
del  mass , f0 , saturation , loss_angle , moi


# %%
# Standard Filter F1
# ~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

mass = 91.31
f0 = 0.250
saturation = -1e-3
loss_angle = 1e-4
moi = se.Matrix(  [ [ *utils.con( 3.8399 , 0.61 , 0 ) ] , [ *utils.con( 0.61 , 3.8399 , 0 ) ] , [ *utils.con( 0 , 0 , 6.4676 ) ] ] )
pos_F1 = { 'for_GND':utils.center( -13.5e-3 ) , 'for_BF' : utils.center( -24.6e-3 ) }
F1 = utils.GASFilterData( mass = mass , moi = moi , pos = pos_F1 , resonant_frequency = f0 , saturation = saturation  , loss_angle = loss_angle , shape = shapes.GASFilterShape ) 
del  mass , f0 , saturation , loss_angle , moi

# %%
# Ground GND
# ~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

pos_GND = { 'for_F1' : utils.center(0) }

# pos_GND = { 'for_BF' : utils.center(0) }
# pos_GND = { 'for_IM' : utils.center(71e-3), 'for_IRM' : utils.triangle( 2*158e-3 , -23.5e-3 , '-L') }

GND = utils.GroundData( pos = pos_GND )

# %%
# Specify the physical properties of wires
# -----
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

# %%
# For mirror
# ~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 4
material = materials.piano_wire
diameter =  utils.con(0.2e-3) 
length =  utils.con(587e-3) 
wire_MIR = utils.WireData( number = number , material = material , diameter = diameter , length = length )
del number , material , diameter , length

# %%
# For Recoil Mass
# ~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 4
material = materials.tungsten
diameter =  utils.con(0.6e-3) 
length =  utils.con(587e-3) 
wire_RM = utils.WireData( number = number , material = material , diameter = diameter , length = length )
del number , material , diameter , length

# %%
# For Intermediate Mass
# ~~~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = utils.con( 2e-3 , 2.5e-3 , 2e-3 )
length = utils.con( 26.5e-3 + 545.5e-3 + 26.5e-3 ) # Should be changed to separation with commas
wire_IM = utils.WireData( number = number , material = material , diameter = diameter , length = length )

# %%
# For Intermediate Recoil Mass
# ~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 3
material = materials.maraging_steel
diameter = utils.con( 2.0e-3 )
length = utils.con( 355.0e-3 )
wire_IRM = utils.WireData( number = number , material = material , diameter = diameter , length = length )

# %%
# For Bottom Filter
# ~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = utils.con( 2.5e-3 , 4.5e-3 , 2.5e-3 )
length = utils.con( 26.5e-3 + 513.4e-3 + 26.5e-3 ) # Should be changed to separation with commas
wire_BF = utils.WireData( number = number , material = material , diameter = diameter , length = length )


# %%
# For Standard Filter
# ~~~~~~~~~~~~~~~~~~~
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

number = 1
material = materials.maraging_steel
diameter = utils.con( 3e-3 , 4.5e-3 , 3e-3 )
length = utils.con( 26.5e-3 + 1280e-3 + 26.5e-3 )
wire_F1 = utils.WireData( number = number , material = material , diameter = diameter , length = length )



