import symengine as se
import numpy as np # for element-wise operations on wires with necks
import bigtree as bt
from . import utils
from . import shapes3d


class Ground( bt.Node ):
    '''
    This is the ground.
    '''
    
    names = ['lon' , 'tra' , 'ver' , 'roll' , 'pitch' , 'yaw'] # The same for all instances of derived classes 
    
    def __init__( self , sus , name , data , **kwargs ):
        
        super().__init__(name=name, **kwargs) # Call bigtree node constructor
        self.name = name
        
        self.attachment_points_p = data.pos # w.r.t. the center of mass
        self.load = 0 # Check whether utils.con(0) or None are better

        # Displacement symbolic variables
        s = " ".join( [ item + self.name for item in RigidBody.names ] )
        self.lon, self.tra, self.ver , self.roll, self.pitch , self.yaw = se.symbols( s , real=True )
        self.r = se.Matrix( [ self.lon , self.tra , self.ver ] ) # A column vector
        self.angles = se.Matrix( [ self.roll , self.pitch , self.yaw ] ) # A column vector

        # Write the displacement vectors of the attachment points w.r.t. the world reference system.
        self.attachment_points_r = {} 
        for key , value in self.attachment_points_p.items(): # The key is the name of the set of  atachment points
            self.attachment_points_r[ key ] = [ self.r + utils.rotB2S( self ) * pp  for pp in value ]

        self.body_coords = []
        self.float_coords = []
        self.gnd_coords = self.r.T.tolist()[0] + self.angles.T.tolist()[0]

    
    def update( self ):            
        # Calculate the load of the body
        if not self.is_leaf:
            self.load = sum( (child.load+child.mass) for child in self.children )


class RigidBody( Ground ):
    """
    A short description.

    A more wordy description.

    Attributes
    ----------
    attachment_points_p : dict
        A dictionary containing the displacement vectors of the attachment points written in body coordinates w.r.t. the body's center of mass.
        *   Each key is the name (str) of the attachment point set (e.g., "for_IM", "for_MIR").
        *   Each value is a list of column vectors defined as $3 \times 1$ Symengine's MutableDenseMatrix matrices with numeric entries.
        *   For internal use, but accesible for user's inspection.
        
    attachment_points_r : dict
        A dictionary containing the displacement vectors of the attachment points written in world coordinates w.r.t. the origin of the world reference frame.
        *   Each key is the name (str) of the attachment point set (e.g., "for_IM", "for_MIR").
        *   Each value is a list of column vectors defined as $3 \times 1$ Symengine's MutableDenseMatrix matrices with symbolic entries.
        *   For internal use, but accesible for user's inspection.
    """
    
    def __init__( self , sus , name , data , **kwargs ):
        Ground.__init__( self , sus , name , data , **kwargs )
        # self.sus = sus # The suspension the body belongs to, currently not in use.
        self.mass = data.mass 
        self.moi  = data.moi # Moment of inertia, se.Matrix
        self.shape = data.shape # Equals to the object definition itself
        self.shape_instance = None # It will be set to the object instance
        self.link = None # Link instance the body couples with to its parent
        self.link_internal = [] # Empty list for a rigid body
        
        # Velocity symbolic variables
        s = " ".join( [ 'v' + item + self.name for item in RigidBody.names ] )
        self.vlon, self.vtra, self.vver , self.vroll, self.vpitch , self.vyaw = se.symbols( s , real=True )
        self.v = se.Matrix( [ self.vlon , self.vtra , self.vver ] ) # A column vector
        vangles = se.Matrix( [ self.vroll , self.vpitch , self.vyaw ] ) # A column vector
        self.omega = se.Matrix( [ [ 1 ,  0                   , -se.sin( self.pitch )                       ] ,
                                  [ 0 ,  se.cos( self.roll ) ,  se.sin( self.roll ) * se.cos( self.pitch ) ] , 
                                  [ 0 , -se.sin( self.roll ) ,  se.cos( self.roll ) * se.cos( self.pitch ) ] ] ) * vangles

        self.body_coords = self.gnd_coords # Override the assignment given in parent class ``Ground``
        self.gnd_coords = []
        
        # Gravitational potential energy
        self.grav_Ep = self.mass * utils.g * self.ver
        
        # Kinetic energy
        self.Ek = se.Rational(1,2) * ( self.mass * self.v.dot( self.v ) + self.omega.T.dot( self.moi * self.omega ) )
        
        # Orientation of the body and its links for animation
        self.orien_lambda = None
        self.orienw_lambda = None

    def update( self ):
        
        super().update()
        
        # Calculate the load of the external link
        # if not self.is_root: # Ground excluded because it is not supported by a link
        link = self.link
        link.load = self.mass + self.load 
        link.load_single = link.load / link.num # Load of individual links of the set of links
        link.tension = link.load_single * utils.g # Tension in individual links of the set
        self.link.update()


#--------------- Links --------------------#

class Spring:
    """
    Parent class of `Wire`, `Flexure` and `Direct`. It is not directly usable, it is a template.
    """
    def __init__( self , sus , data ):
        '''
        sus is the suspension the wires belong to.
        '''
        self.sus = sus # The suspension the link belongs to, used in class `Wire` in method `calculate_torsion_Ep`.
        self.shape = None
        self.damp_factor = 1 + se.I * data.loss_angle

        self.num = data.number
        self.k_axial = data.k_axial
        self.k_torsion = data.k_torsion
        self.length = data.length # Unstretched length
        self.shape = shapes3d.SpringShape

        self.load = None # Load of the set of springs. In `Spring` and `Wire` used only for printing information on the screen. 
        self.load_single = None # Load of the individual springs. In `Spring` and `Wire` used only for printing information on the screen.
        self.tension = None  # Tension in individual springs
         
        # To be updated by method `calculate_stretched_length` in this class.
        self.l_stretch : float = 0  # Total stretched length of wire.
        
        # Vertical length of the link in equilibrium. Used only to guess the vertical equilibrium positions of the bodies in method `supension.guess_equi_coords`.
        # It must either be given or calculated in a method.In class `Wire`, in method `calculate_stretched_length`, it's set equal to the stretched length assuming
        # the wire is vertical in equilibrium. When it's not vertical an angle is needed, but this hasn't been implemented yet.
        self.vlength = utils.con(0) # Default value

        #----- To be updated by `suspension.connect` method --------# 
        self.r_upper = [] # List with position vectors of the upper attachment points, also in dict `self.body.attachment_points_r`, but gathered here for ease of access.
        self.r_lower = [] # List with position vectors of the lower attachment points, also in dict `self.body.attachment_points_r`, but gathered here for ease of access.
        self.angles_lower = None
        self.angles_upper = None
        # self.body = None # Write here why we need this.
        
        # For calculating the axial and torsional potential energies, and for the animation. To be updated in method `calculate_geometry`
        self.r_diff = [] # List with vectors `self.r_upper - self.r_lower`, i.e., vectors point upwards.
        self.norm_diff = [] # List with the norms of the elements of `self.r_diff`.

        # Elastic potential energy dictionary
        self.Ep_dict = {'axial': { 'damp' : self.damp_factor , 'energy'  : utils.con(0) , 'master' : None } ,
                        'torsion'   : { 'damp' : self.damp_factor , 'energy'  : utils.con(0) , 'master' : None } ,
                        'bend'     : { 'damp' : utils.con(0) , 'energy'  : utils.con(0) , 'master' : None } }

    def update( self ):
        """
        """
        # `calculate.stretched_length` in only useful in this class for
        # guessing equilibrium values. In derived class `Wire` it is overriden.
        self.calculate_stretched_length() 
        self.calculate_geometry()


    def calculate_stretched_length( self ):
        """
        L0 and k are scalars, not numpy arrays
        """
        T = self.tension     # Tension in the individual wire
        L0 = self.length     # Unstretched original length 
        k = self.k_axial
        self.l_stretch = L0 + T / k 
        self.vlength = self.l_stretch # Estimate of the vertical length in equilibrium.
        print( 'vlength spring:' , float(self.vlength) ) ####################################################################################################33

    def calculate_geometry( self ):
        """
        Calculates the vector differences between attachment points and their norms.

        These quantities are required to calculate the axial and torsional potential energies,
        and for the animation of the wires.

        Notes
        -----
        Can be called after `suspension.connect`, and therefore, it's called in `suspension.update` via `link.update`.
        """
        for index in range( self.num ):
            
            r_diff = self.r_upper[ index ] - self.r_lower[ index ] # This vector points upwards
            norm_diff = se.sqrt( r_diff.dot( r_diff ) )
            
            self.r_diff.append( r_diff )
            self.norm_diff.append( norm_diff )

    # Currently not in use
    def calculate_bending_Ep( self ):
        return utils.con(0) # Symbolic zero

    # Method currently used for derived classes `Wire` and `Spring`.
    # For classes that don't require it, override it with:
    #
    # def calculate_axial_Ep( self ):
    #     return utils.con(0) # Symbolic zero
    #
    def calculate_axial_Ep( self ):
        '''
        Calculate elastic potential energy
        '''
        add = 0
        for index in range( self.num ):
            add = add + ( self.norm_diff[index] - self.length )**2 
        total = se.Rational( 1 , 2 ) * self.k_axial * add
        self.Ep_dict['axial']['energy'] = total
        return total

    # Method currently used for derived classes `Wire` and `Spring`.
    # For classes that don't require it, override it with:
    #
    # def calculate_torsion_Ep( self ):
    #     return utils.con(0) # Symbolic zero
    #
    def calculate_torsion_Ep( self ):
        """
        Requires knowledge of the equlibrium positions.
        """
        add = 0
        angles_diff = self.angles_upper - self.angles_lower
        for index in range( self.num ) :
            n = ( self.r_diff[ index ] / self.norm_diff[ index ] ).subs( self.sus.equi_coords_dict ) # Unit vector along the wire, pointing upwards and in equilibrium. 
            add = add + angles_diff.dot( n ) ** 2
        total = se.Rational( 1 , 2 ) * self.k_torsion * add
        self.Ep_dict['torsion']['energy'] = total
        return total

    # To generate a dictionary with parameter values for the animation.
    # To be tailored to the specific vpython shape of the derived class
    # It must return a dictionary that will be passed as **kwargs in method `anime.show_anime`.
    # def shape_parameters( self ):
    #     return {}

    def shape_parameters( self ):
        """
        """
        param = {}
        # dim = self.body.shape_instance.shape.size # This is a vpython vector, whose elements can only be accessed with dot notation.
        param[ 'min_dim' ] = 25e-3 # min( dim.x , dim.y ) # Minimum dimension in L and T of the box surrounding the object that hangs from the spring.
        return param

      
class Wire( Spring ):
    '''
    Currently only wires with circular cross sections are supported
    '''
    def __init__( self , sus , data ):
        
        Spring.__init__( self , sus , data )
        self.num = data.number # Overriding the default value of 1 set in parent class
        self.material : str = data.material

        # In the case of receiving a scalar, `np.atleast_1d` makes the array 1D so it's subscriptable.
        self.ll : np.array = np.atleast_1d( np.array( data.length , dtype=object ) )  # Segment lengths unstretched
        self.dd : np.array = np.atleast_1d( np.array( data.diameter , dtype=object ) ) # Segment diameters
        self.ll_stretch : np.array = np.array([]) # Numpy array with the stretched lengths of the link segments (for wires with necks).

        # Elementwise operations using numpy arrays
        self.AA = se.pi * self.dd**2 * se.Rational( 1 , 4 ) # Segment's cross section areas
        self.JJ = se.pi * self.dd**4 * se.Rational( 1 , 64 ) # Segment's 2nd moments of area
        self.JJee = se.pi * self.dd**4 * se.Rational( 1 , 32 ) # Segment's torsional constants

        # To be updated by `calculate_torsion_stiffness` in this class.
        self.kk_torsion : np.array = np.array([]) # Numpy array with the torsional spring constants of the wire segments.

        self.shape = shapes3d.WireShape
        
    # -------- update method --------------#

    def update( self ):
        """
        """
        self.calculate_axial_stiffness()
        self.calculate_stretched_length() # Useful for guessing equilibrium values and torsional stiffness
        self.calculate_geometry()
        self.calculate_torsion_stiffness()
        
    #--------- Methods to be called by the wire's `update` method --------------#

    def calculate_axial_stiffness( self ):
        '''
        '''
        E = self.material.young_modulus
        A = self.AA # Segment cross section areas
        L0 = self.ll # Segment lengths
        self.kk_axial = E * A / L0 # Elementwise operations using numpy arrays
        self.k_axial = utils.kk_series( self.kk_axial ) # Springs added in series

    
    def calculate_stretched_length( self ):
        """
        Calculate the stretched length of the wire and, for wires with necks, of its segments too.

        The individual lengths of segments are required for calculating the torsional stiffness. 
        """
        T = self.tension     # Tension in the individual wire
        L0 = self.ll         # Unstretched original lengths of segments
        k = self.kk_axial
        self.ll_stretch = T / k # Element-wise operations using numpy arrays
        ### print( np.sum( self.ll_stretch ).n(10) ) #######################################################################################################################3
        self.l_stretch = np.sum(L0) + np.sum( self.ll_stretch ) # Sum of the stretched segments
        self.vlength = self.l_stretch # Estimate of the vertical length in equilibrium. In case the link is not supposed to be vertical,
                                      # its projection on the vertical should be given here.


    def calculate_torsion_stiffness( self ):
        """
        """
        # self.calculate_stretched_length()
        G = self.material.shear_modulus
        Je = self.JJee # Segment torsional constants
        T = self.tension # Tension in the individual wire
        J = self.JJ # Segment 2nd moment of area
        A = self.AA # Segment cross section areas
        L = self.ll_stretch
        self.kk_torsion = ( G * Je + T * J / A ) / L # Element wise operations using numpy arrays
        self.k_torsion = utils.kk_series( self.kk_torsion ) # Springs added in series        



#------------ Flexible bodies ----------------#

class InternalSprings:
    
    def __init__( self ):

        # Create the spring instances
        spring_data = utils.SpringData( number = 1 , k_axial = None , length = utils.con(0) , loss_angle = 1e-4 ) ################### Why is the loss angle set to 1e-4 here?
        self.springs = [ Spring( self.sus , data = spring_data ) for _ in range( self.num ) ]

        # Rotation matrix
        rot = utils.rotB2S( self )
        
        # Connect the springs and add them to the list link.internal
        for idx , link in enumerate( self.springs ):
            spr_r_copy = se.Matrix( self.spr_r[idx].tolist() ) # Position of spring in global coordinates, deepcopy does not work on symengine matrices.
            link.r_upper = [ spr_r_copy ]
            link.r_lower = [ spr_r_copy + rot * self.dir_p[idx] ] # self.dir_p is in local coordinates.
            self.link_internal.append( link ) 

        # Cross product with the body's angular velocity. This matrix is already in RigidBody, adapt so it's not written again here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        omegax = se.Matrix( [ [  0             , -self.omega[2] ,   self.omega[1] ] ,
                              [  self.omega[2] ,  0              , -self.omega[0] ] ,
                              [ -self.omega[1] , self.omega[0] ,   0 ] ] )
        
        # Velocity of the point masses that represent the masses of the massive springs
        half = se.Rational(1,2)
        self.ratio = ratio = utils.con(1/2)
        self.v1 = [ self.v + omegax * rot * half * vec_p + rot * half * vec_vp  for vec_p , vec_vp in zip( self.dir_p , self.dir_vp ) ]
        self.v2 = [ self.v - omegax * rot * ratio * vec_p - rot * ratio * vec_vp  for vec_p , vec_vp in zip( self.dir_p , self.dir_vp ) ]

    def update( self ):

        M = self.spring_load / self.num # For a GASFilter num=1, for an IP num=3, for a PreIsolator num=4.
        ratio = self.ratio # Cannot be zero

        for link , f0 , beta , v1 , v2 in zip( self.springs , self.f0 , self.beta , self.v1 , self.v2 ) :
            m1 = utils.con( 0.1 )
            m2 = (-4*M*beta - beta*m1 + m1)/(4*ratio*(beta*ratio + ratio + 1)) # in terms of ( M , beta , m1 , ratio ) # Check whether m2 > 0!!!!!!!!!!!!!!!!
            self.Ek = self.Ek + se.Rational(1,2) * m1 * v1.dot( v1 ) + se.Rational(1,2) * m2 * v2.dot( v2 )
            link.k_axial = ( 2 * se.pi * f0 )**2 * ( M + m1/4 + m2*ratio**2 ) # in terms of ( f0 , M , m1 , m2 , ratio )
            print( f"{self.name}: beta, m1, m2 = {beta.evalf()} , {m1.evalf()} , {m2.evalf()}" ) 
            link.update()
            link.length = - link.l_stretch # This makes the length of the spring zero
        

class GASFilter( RigidBody , InternalSprings ):

    def __init__( self , sus , name , data , **kwargs ):
        
        RigidBody.__init__( self , sus , name , data , **kwargs )

        self.sus = sus

        # self.f0 and self.beta must be in a list, even if they have only one element.
        # It's a requirement for class InternalSprings
        d1 = data.resonant_frequency
        self.f0 = [d1] if type(d1) not in (list,tuple) else d1 # if d1 not a list or tuple take the value and put it in a list, otherwise keep it as a list or tuple.
        d2 = data.saturation
        self.beta = [d2] if type(d2) not in (list,tuple) else d2

        # The body the internal springs holds, i.e., the load of the GAS filter.
        self.spring_body = None # To be updated ``suspension.connect``, used to calculate the spring load in method `update()   ` below

        # Scalar quantifying the spring deformation in local coordinates 
        self.q = se.symbols( 'q' + self.name , real = True ) # Scalar displacement quantifying the deformation of the spring
        self.vq = se.symbols( 'vq' + self.name , real = True ) # Velocity, used in Ek when the spring has mass
        self.direction = se.Matrix( [ 0 , 0 , 1 ] ) # Unit vector along which the motion is constrained in local coordinates
        self.body_coords.append( self.q ) # Add parameter self.q to the list of body coordinates, the spring and the counterweight always have mass.

        # if self.beta[0] == utils.con( 0 ): # A GAS filter has only one spring
        #     print( f"{self.name}: massless spring with float coordinate q{self.name}, " , end="")
        #     self.float_coords.append( self.q ) # Parameter added to the list of float coordinates
        # else:
        #     print( f"{self.name}: spring with mass, " , end="")
        #     self.body_coords.append( self.q ) # Parameter added to the list of body coordinates

        # Two atachment points at the center
        name_center = [ name for ( name , coords ) in self.attachment_points_p.items() if ( coords[0][0] == coords[0][1] == 0 ) ] # Extract the name of the points for which x=y=0
        
        # Identity the lower one from those two
        p0 = self.attachment_points_p[ name_center[ 0 ] ]
        p1 = self.attachment_points_p[ name_center[ 1 ] ]
        if p0[ 0 ][ 2 ] < p1[ 0 ][ 2 ] :
            self.name_for_spring = name_center[ 0 ]
        else :
            self.name_for_spring = name_center[ 1 ]
        print( f"the attachment point at the lower end of the internal spring is called '{ self.name_for_spring }'.")
        
        # For the attachment points of the spring, used in InternalSprings.__init__( self )
        self.num = 1 # Only one spring
        self.spr_r = self.attachment_points_r[ self.name_for_spring ] # List with the position vector of the spring, in global coordinates.
        self.dir_p = [ self.direction * self.q ] # List with direction vectors of the springs, in local coordinates.
        self.dir_vp = [ self.direction * self.vq ] # List with velocity vectors of the springs, in local coordinates.

        # Initialize internal springs
        InternalSprings.__init__( self )

        # Update the lower attachment point with the modifications from InternalSprings
        self.attachment_points_r[ self.name_for_spring ] = self.springs[0].r_lower # self.springs only has one element in the GAS filter

    def central_attachment_point_downstream():
        # In class `GASFilter` return the one which is physically below. 
        return

    def update( self ):

        RigidBody.update( self ) # Update per the parent class RigidBody, which updates the external link.
        
        # This is in the child class because tension=0 must be set for an IP but not for the GAS Filter.
        # However, tension=0 might work for both if the stretched length of the springs is set to a
        # constant value independent of the tension, as this calss is implemented from the begining.
        self.spring_load = self.spring_body.mass + self.spring_body.load
        for link in self.springs: link.tension = self.spring_load * utils.g / self.num # For an IP this tension must be set to zero

        InternalSprings.update( self )
        

class InvertedPendulum( GASFilter ):
    
    # * An Inverted Pendulum could be a horizontal GAS filter
    # * The shape of the IP is defined in shapes3D.py and introduced in the simulation using a data class defined in a utils.py, lilely `InvertedPendulumData()`
    # * What value must self.direction have?
    # * Unlike in the `GASFilter` class, in the IP the attachment point that needs to be identified is the upper one, which is where the load is going to be attached.

    def central_attachment_point_downstream():
        # For the IP return the one which is physically above. 
        return

    pass
