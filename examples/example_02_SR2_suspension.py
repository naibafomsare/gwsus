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
# The necessary libraries are Gwsus, the data classes defined
# in the previous tutorial, and a new one to print information
# about the suspension on the screen: 
import gwsus as sus
import example_01_SR2_data as data
from gwsus import info

# %%
# Suspension instance
# -------------------
# First, the suspension is simply declared with its name:
SR2 = sus.Suspension("SR2")

# %%
# Component instances
# -------------------
# The following step is to create the body instances by passing to the constructor
# their respective names and data classes created in the previous tutorial. Notice that
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
# Names are not required because the software identifies the wires by the body they hold.


# %%
# Suspension assembly
# -------------------
# Then comes the assembly procedure, which establishes connections between the bodies with the wires
# by invoking the :meth:`connect` method:  
SR2.connect( GND , 'for_F1' , F1 , 'for_GND' , wire_F1 )
SR2.connect( F1, 'for_BF' , BF , 'for_F1' , wire_BF )
SR2.connect( BF, 'for_IM', IM, 'for_BF', wire_IM )
SR2.connect( BF, 'for_IRM', IRM , 'for_BF' , wire_IRM )
SR2.connect( IM , 'for_MIR' , MIR , 'for_IM' , wire_MIR )
SR2.connect( IM , 'for_RM' , RM , 'for_IM' , wire_RM )

# %%
# The first two arguments are, in this order, the upper body and the name
# of its attachment point to use. The following two arguments
# are the corresponding elements in the lower body, and the fourth argument is the 
# wire to use. The connection tree with the root at the ground can be shown with:
GND.show()

# %%
# The final step in the assembly procedure is to update the suspension:
SR2.update()

# %%
# This process calculates the body and wire loads, the wire stiffnesses, etc.
# For the GAS filters, it prints the spring and counterweight masses required 
# to achive the transfer function saturation values given by the user. 
# 

# %%
# Assembly information
# --------------------
# The outcome of the update can be displayed in two tables. The loads are shown with:
info.show_info( SR2 , 'load')

# %%
# And information about the links can be printed with:
info.show_info( SR2 , 'links')


# %%
# Equilibrium positions
# ---------------------
# The suspension is now ready for the calculation of the equilibrium positions:
SR2.calculate_equilibrium_positions()

# %%
# This method can take the keyword parameter ``decimal_places``, which defaults to the
# value printed in the output line
#
# .. code-block:: python
#
#     For this task: decimal_places = ...
#
# This parameter sets the precision with which the multiple-precision library,
# Mpmath, will calculate the results. However, depending on the complexity of
# the system, it may be necessary to reduce it. This is alright as long as it is
# not larger than, say, a fraction of a micrometer or so.

# %%
# The values of the equlibrium positions can be printed with:
info.print_equilibrium_positions( SR2 )

# %%
# This method may take a keyword parameter ``n_tables`` for the number of adjacent tables into which
# the results can be split when printed.

# %%
# Mass and stiffness matrices
# ---------------------------
# These matrices represent the linearization of the system around the
# equilibrum positions. The calculation of the mass matrix prints
# information that may be useful:
SR2.calculate_mass_matrix()

# %%
# Next, for the purposes of the later calculating the eigenvectors,
# it is suitable to calculate the stiffness matrix without
# structural damping by setting ``with_damping = False``: 
SR2.calculate_stiffness_matrix( with_damping = False )

# %%
# As the output heading indicates, for calculating transfer functions
# it is necessary to set ``with_damping = True``.
#
# Both of the above functions take the boolean keyword argument ``verbose`` to indicate whether
# information should be printed for troubleshooting. Its default value is ``False``.

# %%
# Frequencies and shapes of resonance modes
# -----------------------------------------
#

SR2.calculate_eigenvectors()
info.print_eigenfreq( SR2 , 4 )


# %%
# Animation
# ---------
#

sus.prepare_anime( SR2 )

n = 32
info.print_eigen( SR2 , n )

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