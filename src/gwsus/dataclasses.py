'''
These data classes group the physical parameters
of bodies, springs and wires in a suitable way to pass
them to the constructors of classes in module ``components``. 
'''

from dataclasses import dataclass, field
from typing import List
import numpy as np
from .utils import con

@dataclass
class GroundData:
    '''Data class that gathers the positions of the attachment points at the ground.'''
    
    pos: dict 
    '''
    Dictionary with the position vectors of the attachment points.
    
    * Key: name of the attachment point set, e.g. ``'for_F1'``, ``'for_MIR'``, ``'for_IM'``, etc.   
    
    * Value: list returned by function ``center()``, ``rectangle()`` or ``triangle()``.
    '''

@dataclass
class BodyData( GroundData ):
    '''
    Data class that gathers the body's physical parameter values.
    '''
    
    mass : object
    '''
    Mass of body in kg. The user can specify it as ``float`` and it will be
    automatically converted to a Symengine rational.
    '''
    
    moi : object
    '''
    Moment of inertia returned by function ``moi()`` or ``moi_diagonal()``.
    **The former has not been implemented yet**.
    '''
    
    shape : object
    '''Equals to the definition of the VPython 3D object class, not to an instance of the class.'''

    def __post_init__( self ):
        '''Convert ``mass`` to ``symengine.lib.symengine_wrapper.Rational``.'''
        self.mass = con( self.mass )

@dataclass
class GASFilterData( BodyData ):
    '''
    Data class that gathers the physical parameters of a GAS filter.
    
    Parameters ``pos`` and ``mass`` are described in parent classes 
    ``GroundData`` and ``BodyData`` respectively.
    '''
    
    resonance_frequency: object  # resonant frequency in Hz 
    '''
    Resonance frequency in Hz. The user can specify it as ``float`` and it will
    be automatically converted to a Symengine rational.
    '''
    
    saturation : object
    '''
    Saturation value of the displacement transfer function. The user can
    specify it as ``float`` and it will be automatically converted to a Symengine rational.
    The sign of the value determines whether the notch appears or not.
    '''

    loss_angle: object
    '''
    Loss angle of the spring constant. The user can specify it as ``float`` and it will
    be automatically converted to a Symengine rational.
    '''

    def __post_init__( self ):
        '''Convert ``mass``, ``resonance_frequency``, ``saturation`` and ``loss_angle``
        to ``symengine.lib.symengine_wrapper.Rational``.'''
        self.mass = con( self.mass )
        self.resonance_frequency = con( self.resonance_frequency )
        self.saturation = con( self.saturation )
        self.loss_angle = con( self.loss_angle )

#     def empty_matrix_3x3():
#         return se.zeros(3)
#     moi : se.Matrix = field(default_factory=empty_matrix_3x3)


@dataclass( kw_only = True )
class SpringData:
    '''
    Data class that gathers the physical parameters of a spring.
    '''
    
    number: int
    '''
    Number of links in the set.
    '''
    
    length: object # Why isn't this length converted to a se.Rational?
    
    loss_angle: object = con(0)

    # WireData is child of SpringData, so default values (that will be later overriden)
    # are needed here for when ``Wire`` calls the ``Spring`` constructor.
    k_axial: object = None 
    k_torsion: object = None


# @dataclass( kw_only = True )
# class SpringZero:
#     direction: object
#     resonance_frequency: object
#     saturation: object
#     loss_angle: object


@dataclass( kw_only = True )
class WireData( SpringData ):
    '''
    This is a description.
    '''
    
    material: str
    '''Wire material'''
    
    diameter: List[ object ]
    '''Wire diameter'''
    
    length: List[ object ] 
    '''Wire length'''

    def __post_init__( self ): 
        '''
        Initialize the loss angle value to that of the material,
        and convert ``diameter`` and ``legnth`` to Symengine rationals.
        
        Because material is not know beforehand, it can only
        be set during initialization.
        '''
        self.diameter = con( self.diameter )
        self.length = con( self.length )
        self.loss_angle = self.material.loss_angle

    


    # material: SimpleNamespace = field(
    #     default_factory=lambda: SimpleNamespace( loss_angle=0 )
    # )

    # def __post_init__( self ): # Change the loss angle default value during initilization
    #     self.material.loss_angle = self.loss_angle


