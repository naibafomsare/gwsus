"""
===========
Suspensions
===========

.. warning::

    Documentation under construction   
    This section is incomplete and subject to change.

Using the data class instances declared previously, this tutorial
first illustrates how to declare the objects representing the rigid bodies
and how to assemble them into a suspension. Next, it describes how to calculate
the frequencies and shapes of resonance modes and how to generate interactive 
3D animations of such modes.
"""

# %%
# Import libraries
# ----------------------------
# The necessary libraries are Gwsus and the data classes defined
# in the previous tutorial: 
import gwsus as sus
import example_01_SR2_data as data

# %%
# Suspension instance
# -------------------
# First, the suspension is simply declared with its name:
SR2 = sus.Suspension("SR2")

# %%
# Component instances
# -------------------
# The following step is to create the body instances by passing to the constructor
# their respective names and data classes with physical specifications. Notice that
# different constructors are used for the ground, GAS filters and rigid
# bodies without internal springs.
GND = sus.Ground( 'GND', data.GND )

F1  = sus.GASFilter( 'F1', data.F1 )
BF  = sus.GASFilter( 'BF', data.BF )

IM  = sus.RigidBody( 'IM', data.IM )
IRM = sus.RigidBody( 'IRM', data.IRM )
MIR = sus.RigidBody( 'MIR', data.MIR )
RM  = sus.RigidBody( 'RM', data.RM )

# %%
# The GAS filter initialization method prints the name of the attachment point
# at the end of the filter's internal spring. 

# %%
# Wire instances
# --------------
# A similar procedure is carried out for the wires, with the only
# difference of not requring names: 
wire_MIR = sus.Wire( data.wire_MIR )
wire_RM = sus.Wire( data.wire_RM )
wire_IM = sus.Wire( data.wire_IM )
wire_IRM = sus.Wire( data.wire_IRM )
wire_BF = sus.Wire( data.wire_BF )
wire_F1 = sus.Wire( data.wire_F1 )

# %%
# Internally, the software identifies the wires by the body they hold.


# %%
# Suspension assembly
# -------------------
# Then comes the suspension assembly. 
SR2.connect( GND , 'for_F1' , F1 , 'for_GND' , wire_F1 )
SR2.connect( F1, 'for_BF' , BF , 'for_F1' , wire_BF )
SR2.connect( BF, 'for_IM', IM, 'for_BF', wire_IM )
SR2.connect( BF, 'for_IRM', IRM , 'for_BF' , wire_IRM )
SR2.connect( IM , 'for_MIR' , MIR , 'for_IM' , wire_MIR )
SR2.connect( IM , 'for_RM' , RM , 'for_IM' , wire_RM )

# %%
# Show the connection tree: 
GND.show()

# %%
# Update the suspension:
SR2.update()

# %%
# Assembly information
# --------------------
# Loads:
sus.show_info( SR2 , 'load')

# %%
# Links:
sus.show_info( SR2 , 'links')


# %%
# Equilibrium positions
# ---------------------
#
SR2.calculate_equilibrium_positions()
sus.print_equilibrium_positions( SR2 )

# %%
# Mass and stiffness matrices
# ---------------------------

SR2.calculate_mass_matrix()
SR2.calculate_stiffness_matrix( with_damping = False )


# %%
# Frequencies and shapes of resonant modes
# ----------------------------------------
#

SR2.calculate_eigenvectors()
sus.print_eigenfreq( SR2 , 4 )


# %%
# Animation
# ---------
#

sus.prepare_anime( SR2 )

n = 32
sus.print_eigen( SR2 , n )

# %%
# Sphinx-Gallery will run the following block, capture the console output, 
# and automatically embed the generated plot directly into the HTML page!

sus.show_anime( SR2 , n )


# %%
# .. image:: ../_static/SR2_still_anime.png
#    :alt: Three-dimensional visualization of the mechanical system
#    :align: center
#    :width: 50%

# %%
# Sphinx-Gallery will run the following block, capture the console output, 
# and automatically embed the generated plot directly into the HTML page!