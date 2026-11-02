from dataclasses import dataclass
import symengine as sy
from . import utils
# from symengine import S

#########################
## Material properties ##
#########################

@dataclass
class Material:
    name: str
    young_modulus: object
    poisson_ratio: object
    loss_angle: object
    shear_modulus: object = None # Derived parameter, so it's not needed in __init__
    
    def __post_init__(self): # Calculate value after __init__
        self.shear_modulus = ( self.young_modulus / ( 2 * ( 1 + self.poisson_ratio ) )  )
    
###############################################################
    
# maraging_steel = Material( name = 'maraging_steel' , young_modulus = utils.con(195e9*1e4) , poisson_ratio = utils.con(0.32) , loss_angle = utils.con(1e-4) ) # 1e4 stiffer!

maraging_steel = Material( name = 'maraging_steel' , young_modulus = utils.con(195e9) , poisson_ratio = utils.con(0.32) , loss_angle = utils.con(1e-4) ) 

piano_wire = Material( name = 'piano_wire' , young_modulus = utils.con(200e9) , poisson_ratio = utils.con(0.3) , loss_angle = utils.con(1e-4) ) 

tungsten = Material( name = 'tungsten' , young_modulus = utils.con(411e9) , poisson_ratio = utils.con(0.28) , loss_angle = utils.con(1e-4) ) 
