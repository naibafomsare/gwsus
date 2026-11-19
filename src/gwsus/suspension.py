import symengine as se
import sympy as sp
import mpmath as mpm # for multiple precision numerical mathematics
import numpy as np # for element-wise operations on wires with necks and for an early version of the eigenvalue problem
import bigtree as bt
from collections import defaultdict
import time
from . import components
from . import utils
from . import shapes3d
from sympy import lambdify as splambdify # to lambdify using mpmath module, which is not possible in Symengine.
from sympy import sympify
import copy

# from types import SimpleNamespace

from termcolor import cprint

import math

# Set precision to certain number of decimal places
# It shoud not be set inside the class because mpmath uses the global context
# mpm.mp.dps = 150

import symengine as se
import mpmath as mp

mp.mp.dps = 100


class Suspension:
    """
    """
    
    def __init__( self , name ):
        
        self.name = name
        self.root = None # For the root node
        
        self.body_list = [] # populated in update()
        
        # Ordered lists by type of coordinate
        self.coords_list = []
        self.vel_coords_list = []
        self.body_coords_list = None
        self.float_coords_list = None
        self.gnd_coords_list = None
        self.nbody = 0 ; self.nfloat = 0 ; self.ngnd = 0 # To be updated in create_coords_list()

        self.body_coords_vector = None
        self.float_coords_vector = None
        
        self.link_axial_Ep = 0 # Total wire axial potential energy
        self.link_torsion_Ep = 0 # Total wire torsional potential energy
            
        self.grav_Ep = 0 # Total gravitational potential energy # To be updated by collect_gravitational_potential_energy()
        self.Ep = 0 # Total potential energy of the suspension, without damping for now.
        self.Ek = 0 # Total kinetic energy of the suspension.
        
        self.gnd0 = None # A dictionary, to be updated in `update`.
        
        self.eigen_dict = defaultdict(dict)
        
        # Equilibrium coordinates guess
        self.equi_coords_guess_dict = None
 
        self.equi_coords_dict = None
        '''A dictionary with the calculated equilibrium coordinates, to use with sympy substitute method.'''
        
        self.M_matrix = None
        self.K_matrix    = None 
        self.C_XQ_matrix = None
        self.C_XS_matrix = None
        self.Q_matrix    = None
        self.C_QS_matrix = None
        self.S_matrix    = None

        self.K_eff_matrix = None # K_matrix with the effect of float coordinates
        self.C_XS_eff_matrix = None # C_XS_matrix with the effect of float coordinates
        self.E_matrix = None # This is called the equation of motion matrix
        self.TF_matrix = None # Transfer function matrix

        self.w = se.symbols( 'w' , real=True )
        
        
        # For displaying information
        self.indent = ''
        
        self.P = None ################################################################################################################ For troubleshooting

        # Dictionary to store transfer functions
        # For TFs from ground coordinates to body coordinates
        self.tf_dict = None # 
        
        # The dictionary for the TFs from generalized forces to body coordinates still has to be declared here
        
    #------------------ Connect --------------------------#
        
    def connect( self , body_upper , name_point_upper , body_lower , name_point_lower , link ):
        """
        Establishes a connection between attachment points via a link. 
        
        Parameters
        ----------
        body_upper : gwsus.RigidBody
            Body connected to the upper end of the link.
        name_point_upper : str
            Name of the attachment point set in the upper body.
        body_lower : gwsus.RigidBody
            Body connected to the lower end of the link.
        name_point_lower : str
            Name of the attachment point set in the lower body.
        link : gwsus.Spring or gwsus.Wire
            Link used for connecting the attachment points.
        """

        body_upper >> body_lower # Connects the bodies with Bigtree
        self.root = body_upper.root # To allow finding the overall root
        body_lower.link = link # By practice in Bigtree, the link instance is kept with the lower body
        link.sus = self # The link knows what suspension it belongs to. Used in class `Wire` in method `calculate_torsion_Ep`.

        for index in range( link.num ): # For each individual link in the set of links
            link.r_upper.append( body_upper.attachment_points_r[ name_point_upper ][ index ] ) # Upper attachment points
            link.r_lower.append( body_lower.attachment_points_r[ name_point_lower ][ index ] ) # Lower attachment points
        link.angles_upper = body_upper.angles
        link.angles_lower = body_lower.angles
        # link.body = body_lower # The link knows which body it belongs to 
                               # currently used only to determine the diameter of springs in the animation, which maybe should be done by the body instance.

        # For GAS filters we need to know which body is hanging from its spring,
        # because it may have more than one child, e.g. as in the Bottom Filter.
        if type( body_upper ) == components.GASFilter:
            if name_point_upper == body_upper.name_for_spring:
                body_upper.spring_body = body_lower
                
    #---------- Update suspension information after connecting components ----------------#
    
    def update( self ):
        """
        Method to calculate the loads of bodies and tensions and stiffnesses of links.

        To be excecuted after all the connections have been established with method `connect`.
        """
        root = self.root
        self.body_list = list( bt.preorder_iter( root ) ) # Generate self.body_list, from top to bottom
        for body in bt.postorder_iter( root ): body.update() # From bottom to top so the loads of children are calculated before those of the parents.

        # Dictionary with ground coordinates to zero
        gndk = self.root.gnd_coords
        gndv = [ utils.con(0) ] * len( gndk )
        self.gnd0 = dict( zip( gndk , gndv ) ) 
        
    #--------- Calculate different types of energy --------------------#
                
    def calculate_link_axial_Ep( self ):
        """
        Calculates the total wire elastic axial potential energy.
        
        Collects and adds algebraic wire axial elastic potential energy terms for all wires,
        assigning the total sum to ``self.link_axial_Ep``.

        Returns
        -------
        self.link_axial_Ep : type
            Algebraic expression of the total gravitational potential energy.

        Notes
        -----
        Typically for internal use, but can be called by user.
        """
        print( self.indent + 'Calculating the total wire axial elastic potential energy... ' , end="")
        add = 0                         
        for body in self.body_list[1:]: # Skip the root, which doesn't have a wire
            ene = body.link.calculate_axial_Ep() # For external links
            add = add + ene
            for link in body.link_internal: # For internal links
                ene = link.calculate_axial_Ep()
                add = add + ene
        self.link_axial_Ep = add
        print("Done.")
        return add
    
    def calculate_link_torsion_Ep( self ):
        """
        Calculates the total link elastic torsional potential energy.
        
        Collects and adds algebraic torsional elastic potential energy terms for all links,
        assigning the total sum to `self.link_torsion_Ep`.

        Returns
        -------
        self.link_torsion_Ep : type
            Algebraic expression of the total gravitational potential energy.
        """
        print( self.indent + "Calculating the total link torsional elastic potential energy... " , end="")
        add = 0          
        for body in self.body_list[1:] : # Skip the root, which doesn't have a link, also internal links don't have torsional Ep
            add = add + body.link.calculate_torsion_Ep()
        self.link_torsion_Ep = add
        print("Done.")
        return add
      
    def calculate_grav_Ep( self ):
        """
        Calculates the total gravitational potential energy.
        
        Collects algebraic gravitational potential energy terms for all bodies,
        assigning the total sum to self.grav_Ep.

        Returns
        -------
        self.grav_Ep : type
            Algebraic expression of the total gravitational potential energy.

        Notes
        -----
        Typically for internal use, but can be called by user.
        """
        print( self.indent + "Collecting gravitational potential energy terms... " , end="")
        add = 0    
        for body in self.body_list[1:]: # Skip the root, which doesn't contribute to the total potential energy
            add = add + body.grav_Ep
        self.grav_Ep = add
        print("Done.")
        return add
    
    def calculate_Ek( self ):
        """
        Calculates the total kinetic energy.
        
        Collects and adds algebraic kinetic energy terms for all bodies, assigning the result to self.Ek.

        Returns
        -------
        self.Ek : type
            Algebraic expression of the total kinetic energy.

        Notes
        -----
        Typically for internal use, but can be called by user.
        """
        print('Collecting kinetic energy terms... ' , end="")
        add = 0                     
        for body in self.body_list[1:] : # Skip the root, which doesn't contribute to the total kinetic energy
            add = add + body.Ek
        self.Ek = add
        print("Done.")
        return add
                
    def calculate_Ep( self ):
        """
        Calculates the addition of gravitational and axial elastic potential energies.
        
        Adds algebraic expressions of the gravitational and axial elastic potential
        energies of all bodies and links, assigning the result to `self.Ep`. The
        rotational potential energies of links is not calculated here because it 
        requires knowledge of the equilibrium positions of their ends.

        Returns
        -------
        self.Ep : type
            Algebraic expression of the total potential energy.

        Notes
        -----
        Typically for internal use, but can be called by user.
        """
        print( self.indent + 'Calculating the total potential energy...')
        ind = self.indent ; self.indent = self.indent + "\t"
        e1 = self.calculate_grav_Ep()
        e2 = self.calculate_link_axial_Ep()
        # The method `calculate_link_torsion_Ep` is called at the end of method `calculate_equilibrium_positions`
        self.Ep = e1 + e2
        self.indent = ind
        return self.Ep
    
    #--------------------------------------------------------#
                
    def create_coords_list( self ):
        '''
        Orders the coordinates according to type in a list.
        [ body, float , ground ]
        '''
        print("Compiling position and velocity coordinates..." , end="")
        self.tab = "\t"
        
        add1 = [] ; add2 = [] ; add3 = []
        
        for body in self.body_list:
            add1 = add1 + body.body_coords
            add2 = add2 + body.float_coords
            add3 = add3 + body.gnd_coords
            
        self.nbody =  len( add1 )
        self.nfloat =  len( add2 )
        self.ngnd =  len( add3 )
        
        self.body_coords_list = add1        
        self.float_coords_list = add2
        self.gnd_coords_list = add3        
        self.coords_list = add1 + add2 + add3 

        
        # It's easier to produce the velocities list from add1 rather than collecting the symbols.
        # Float coordinates don't have mass, and therefore, they should not be in self.vel_coords_list,
        # which will be used to calculate the mass matrix.
        self.vel_coords_list = [ se.symbols( 'v' + item.name , real=True ) for item in add1 ]

        # To allow the calculation of float coordinates in terms of the body coordinates in method `calculate_stiffness_matrix`,
        # using the equation of motion for float coordinates. Required for the animation only, at least so far.
        self.body_coords_vector = se.Matrix( [ coord - self.equi_coords_dict[ coord ] for coord in add1 ] )
        
        print("Done.")
        print( self.tab + 'Number of body coordinates:' , self.nbody )
        print( self.tab + 'Number of float coordinates:' , self.nfloat )
        print( self.tab + 'Number of ground coordinates:' , self.ngnd )
    
    #-----------------------------------------------------------------#
    
    def guess_equi_coords( self ):
        
        print( self.indent + "Guessing the values of the equilibrium coordinates... " , end='')
        # Ground coordinates to zero, the vertical position of the ground is the reference.
        # The .copy() is to create a different dictionary, otherwise self.gnd0 will be modified too!
        self.equi_coords_guess_dict = self.gnd0.copy() 

        for body in self.body_list[1:] : # From top to bottom w/o ground
            for pos in body.r[:2]: # lon and tra
                self.equi_coords_guess_dict[ pos ] = utils.con(0)
            for theta in body.angles : # The three angles
                self.equi_coords_guess_dict[ theta ] = utils.con(0)

            # For vertical
            subs_dict = self.equi_coords_guess_dict
            upper_attachment_point_p = body.link.r_upper[0][2].subs( subs_dict )
            lower_attachment_point_p = body.link.r_lower[0][2].subs( subs_dict ) - body.ver
            l = upper_attachment_point_p - body.link.vlength - lower_attachment_point_p
            self.equi_coords_guess_dict[ body.ver ] = l 
            ######## print(  body.name, body.ver, upper_attachment_point_p.n(6), lower_attachment_point_p.n(6), body.link.vlength.n(6), l.n(6) ) ####################################

            # For bodies with internal links, i.e, instances of GASFilter and InvertedPendulum.
            # If it's exactly zero an error is produced in finding the equilibrium position, maybe because the grad Ep is not simplified.
            if type( body ) in ( components.GASFilter , ): self.equi_coords_guess_dict[ body.q ] = utils.con(1e-20) 
  
        print("Done.")

        
    def calculate_equilibrium_positions( self, decimal_places: int = int(mpm.mp.dps/2) ):
        '''
        '''
        current = self.equi_coords_dict
        if current != None:
            print('The equilibrium positions have already been calculated.')
            return current
        print("Let's calculate the equilibrium positions...")
        # self.indent="\t"
        
        start_time = time.perf_counter()

        tol = mp.mpf(10) ** (-decimal_places + 5)
        print(f'Tolerance: {tol}')

        # Guess equilibrium coordinate values
        self.guess_equi_coords()
        
        # Check wheter the total potential energy has been calculated
        if self.Ep == 0 :
            Ep = self.calculate_Ep()
            print("\tI'm reasonably assuming that the link elastic torsional potential energies are zero at equilibrium.")
        else :
            Ep = self.Ep

        # For setting some yaw variables to zero
        coords0 = self.gnd0.copy()
        
        # For bodies hanging from a single link strand,
        # set the yaw variables equal to the yaw of their
        # parents so mpmath.findroot() does not attempt to optimize them
        # Because the torsional potential energy is not included in the calculation
        # of the equilibrium positions, there's no restriction on those DoF.
        # The `for` loop is without the ground, and must go from top to bottom
        # so the substituted yaw coordinate of a body propagates to its children.
        for body in self.body_list[1:]:
            if body.link.num == 1:
                coords0[ body.yaw ] = coords0[ body.parent.yaw ] 

        # Substitute with numeric values the variables that don't
        # participate in the optimization. 
        Ep = Ep.subs( coords0 )

        # Symbols in Ep, sorted for reproducibility.
        args = sorted( Ep.free_symbols , key=lambda sym : sym.name )

        # Calculate gradient
        print( self.indent + 'Calculating symbolic gradient...', end="\n" )
        grad = [ se.diff( Ep , symbol ) for symbol in args ]

        # print( self.indent + 'Calculating the Jacobian of the gradient...' , end="\n" )
        # grad_matrix = se.Matrix( len(args), 1 , grad )
        # vars = se.Matrix(len(args), 1, args)
        # jac_matrix = grad_matrix.jacobian( vars )
        # jaco = jac_matrix.tolist()

        with mpm.workdps(decimal_places):
            # print(f"For this task: decimal_places = {mpm.mp.dps}.")
            
            # Lambidify with Sympy to use mpmath
            # In case you need to call this function directly, you need
            # to unpack the argument: grad_lambda( *argument )
            print( 'Converting gradient from Symengine to Mpmath... ', end='' )
            start_time_2 = time.perf_counter()
            grad_lambda = splambdify( args, grad, cse=True, modules='mpmath') 
            end_time_2 = time.perf_counter()
            elapsed_time_2 = end_time_2 - start_time_2
            print( self.indent + f"{elapsed_time_2:.4f} seconds.")
            # jaco_lambda = splambdify( args , jaco  , modules='mpmath', cse=True)  
    
            guess_dict = self.equi_coords_guess_dict
            guess = []
            
            # Compile the equilibrium guessed values into a list of
            # mpmath floats to pass it `mpm.findroot`. In the same
            # order as in args to pass it to mp.findroot()
            for symbol in args:
                # From symengine rational to string to mpm.mpf
                # with twice as much precision
                guess.append( mpm.mpf( str( guess_dict[ symbol ].n( 2*mpm.mp.dps ) ) ) ) 

             
    
            # Minimize the potential energy
            print(self.indent + 'Minimizing the total potential energy... ' , end="", flush=True )
            start_time_3 = time.perf_counter()
            result = list( mpm.findroot( grad_lambda , guess , solver='mdnewton', tol=tol, maxsteps=1000 ) )
            end_time_3 = time.perf_counter()
            elapsed_time_3 = end_time_3 - start_time_3
            print( self.indent + f"{elapsed_time_3:.4f} seconds.")
            # result = list( mpm.findroot( grad_lambda , guess , J = jaco_lambda ) )
            
            # Remove anything whose magnitude is smaller than the tolerance.
            result = mpm.chop( result , tol=tol) 

            
            result = [ utils.con( str( item ) ) for item in result ] # Convert to Symengine Rational
            print("Done.")

        
        # Populate a dictionary self.equi_coords_dict with the results
        self.equi_coords_dict = dict( zip( args , result ) ) | coords0

        print( self.indent + "Equilibrium positions found.")
        
        # The torsional potential energy is calculated and added to the total
        print("With knowledge of the equilibrium positions, I'm calling for the calculation of the symbolic link torsional potential energies... ")
        self.calculate_link_torsion_Ep()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print( self.indent + f"Elapsed time: {elapsed_time:.4f} seconds.")
 
        self.indent = ""
        print( f"Call {self.name}.print_equilibrium_positions() to see the results.")

    #-------------------------------------------------------------------#
        
    def matrix_2nd_der( self , term , etype : str , verbose = False ):
        '''
        '''
        
        if etype == 'potential':
            sym_list = sorted( term.free_symbols , key=lambda sym : sym.name )
            coords_list = self.coords_list
            subs_dict = self.equi_coords_dict
        elif etype == 'kinetic':
            dummy = term.subs( dict.fromkeys( self.coords_list , 0 ) ) # Set position coordinates to zero so only velicities remain.
            sym_list = sorted( dummy.free_symbols , key=lambda sym : sym.name ) # Get the velocity symbol list without position coordinates  
            coords_list = self.vel_coords_list
            subs_dict = dict.fromkeys( sym_list , 0 ) | self.equi_coords_dict # All velocities are zero in equilibrium
        else:
            raise ValueError("The string argument must be either 'potential' or 'kinetic'.")

        # Index in coords_list for each symbol in sym_list
        index_dict = {}
        for sym in sym_list :
            index_dict[ sym ] = coords_list.index( sym ) 
            
        # Define the matrix of a given size as a list of lists, all elements are zeros.
        size = len( coords_list )
        matrix = [[0 for _ in range(size)] for _ in range(size)]
    
        # Calculate the derivatives
        print( "calculating matrix... " , end="" )
        for idx , ( symi , i ) in enumerate( index_dict.items() ):
            der = se.diff( term , symi ) # derivative w.r.t. the coordinate with index i 
            for ( symj , j ) in list( index_dict.items() )[idx:] :
                der2_sym = se.diff( der , symj ) # Symbolic 
                der2 = der2_sym.subs( subs_dict ) # Numeric
                if sympify( der2 ).has( sp.nan ):
                    if verbose == True:
                        print("\n" + self.indent + f"\tNan detected in element ({coords_list[i]},{coords_list[j]}), I'm trying to solve this... " , end="")
                    der2 = utils.simplify( der2_sym , subs_dict )
                    if sympify( der2 ).has( sp.nan ): print('Failed. ', end='')
                    elif verbose == True: print('Solved. ', end='')
                matrix[ i ][ j ] = der2 
                matrix[ j ][ i ] = der2 
        print("Done.")

        return se.Matrix( matrix )

        
    def calculate_mass_matrix( self , verbose = False ):
        '''
        '''
        print("Let's calculate the mass matrix...")
        start_time = time.perf_counter()
        
        if self.Ek == 0 :
            Ek = self.calculate_Ek()
        else:
            Ek = self.Ek
            
        if self.vel_coords_list == [] :
            self.create_coords_list()
        else:
            print('The list vel.coords_list has already been created.')
        
        self.M_matrix = self.matrix_2nd_der( Ek , 'kinetic' , verbose = verbose )

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds.")
        print(f"Done, call {self.name}.M_matrix to see the result.")

        
    def calculate_stiffness_matrix( self , with_damping = False , verbose = False ):
        '''
        '''
        print("Let's calculate the master stiffness matrix and its submatrices...")

        if with_damping == True: 
            cprint( "The setting `with_damping = True` is suitable for later calculating transfer functions,\nfor calculating eigenvectors set `with_damping = False`." , color=( 152 , 251 , 152) )
        elif with_damping == False:
            cprint( "The setting `with_damping = False` is suitable for later calculating eigenvectors,\nfor calculating transfer functions set `with_damping = True`." , color=( 152 , 251 , 152) )
        
        start_time = time.perf_counter()
        
        if self.equi_coords_dict == None:
            print("The equilibrium coordinates haven't been calculated, I'm calling `self.calculate_equilibrium_positions`.")
            self.calculate_equilibrium_positions()

        
        size = len( self.coords_list )
        P = se.zeros( size , size )

        for body in self.body_list[1:] : # w/o root, which doesn't have a link
        
            print( f"For {body.name}:"  )
            self.indent = "\t"

            for link in [ body.link ] + body.link_internal: # External and internal links

                # Master stifness matrices for the axial elastic potential energies
                current1 = link.Ep_dict['axial']['master']
                # Check whether it's been calculated already
                if current1 == None: # If the corresponding dict entry equals None, calculate the matrix
                    print( self.indent + 'Link axial potential energy: ' , end="" )
                    term1 = link.Ep_dict['axial']['energy']
                    matrix1 = self.matrix_2nd_der( term1 , 'potential' , verbose = verbose )
                    link.Ep_dict['axial']['master'] = matrix1
                else: # Otherwise use the one already there
                    matrix1 = current1
                
                # Master stifness matrices for the torsional elastic potential energies
                current2 = link.Ep_dict['torsion']['master']
                # Check whether it's been calculated already
                if current2 ==  None: # If the corresponding dict entry equals None, calculate the matrix
                    print( self.indent + 'Link torsional potential energy: ' , end="" )
                    term2 = link.Ep_dict['torsion']['energy']
                    matrix2 = self.matrix_2nd_der( term2 , 'potential' , verbose = verbose  )
                    link.Ep_dict['torsion']['master'] = matrix2
                else: # Otherwise use the one already there
                    matrix2 = current2 

                # term3 = link.Ep_dict['bending']['energy']
                # matrix3 = self.matrix_2nd_der( term3 , 'potential' )
                # link.Ep_dict['bending']['master'] = matrix3

                # For some future calculation each matrix below should be multiplied by its damping factor
                if with_damping == True :
                    d1 = link.Ep_dict['axial']['damp'] 
                    d2 = link.Ep_dict['torsion']['damp'] 
                    d3 = link.Ep_dict['bend']['damp']
                else:
                    d1 = d2 = d3 = 1

                # Adds the stiffness matrix of the link to the total matrix of the suspension
                print( self.indent + "Adding these matrices to total... " , end="" )
                P = P + d1 * matrix1 + d2 * matrix2 # + d3 * matrix3
                print("Done.")

        print(f"I have the final master stiffness matrix, you can see it by calling {self.name}.P")
        self.P = P # Mostly for troubleshooting because it's not used.
        
        # Extracts submatrices from the total master stiffness matrix
        print( 'Extracting the relevant submatrices from the master stiffness matrix...' )

        nb = self.nbody
        nbf = nb + self.nfloat
        nbfg = nbf + self.ngnd

        # Matrix[ rows , columns ]
        self.K_matrix    = P[ 0 : nb , 0 : nb ]
        self.C_XS_matrix = P[ 0 : nb , nbf : nbfg ]
        self.S_matrix    = P[ nbf : nbfg , nbf :  nbfg ]
        
        if self.nfloat != 0 :
            
            self.C_XQ_matrix = P[ 0 : nb , nb : nbf ]

            self.Q_matrix    = P[ nb : nbf , nb : nbf ]
            self.C_QS_matrix = P[ nb : nbf , nbf : nbfg ]


            dummy_matrix = self.Q_matrix.inv() * self.C_XQ_matrix.T
            # print( self.Q_matrix , '\n')
            # print( self.Q_matrix.inv() , '\n')
            # print( dummy_matrix )
            
            # Without float coordinates they are equal
            self.K_eff_matrix = self.K_matrix - self.C_XQ_matrix * dummy_matrix
            
            # Without float coordinates they are equal
            self.C_XS_eff_matrix = self.C_XS_matrix - self.C_XQ_matrix * self.Q_matrix.inv() * self.C_QS_matrix

            # Float coordinates in terms of the body coordinates, calculated
            # using the equation of motion for float coordinates.
            # Required for the animation only, at least so far.
            q_eq_vector = se.Matrix( [ self.equi_coords_dict[ coord ] for coord in self.float_coords_list ] )
            self.float_coords_vector = q_eq_vector + dummy_matrix * self.body_coords_vector
            
        else:            
            print( self.indent + "There are no float coordinates, matrices Q, C_XQ, C_QS and related don't exist." )
            
            # Produces ().T.tolist() = [[]], needed in `anime.prepare_animation`
            self.float_coords_vector = se.Matrix( 1 , 0 , [] ).T
            
            # Without float coordinates they are equal
            self.K_eff_matrix = self.K_matrix
            
            # Without float coordinates they are equal
            self.C_XS_eff_matrix = self.C_XS_matrix

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Finished, elapsed time: {elapsed_time:.4f} seconds.")

        
    def calculate_eigenvectors( self , alternative_matrix = None , decimal_places: int = mpm.mp.dps ):
        """
        With mpmath
        """
        start_time = time.perf_counter() 

        if alternative_matrix == None:
            Asym = self.M_matrix.inv() * self.K_matrix # Matrix with symengine rational elements
        else:
            Asym = alternative_matrix

        # tol = mp.mpf(10) ** (-decimal_places + 5)
        # print(f'Tolerance: {tol}')

        # For diagnosis
        # test = Asym
        # for row in test.tolist() :
        #     for ele in row:
        #         if ele.is_real != True:
        #             print( utils.se2mpm(ele, mpm.mp.dps) )
        
        # Scan through matrix elements, convert them to Mpmath and put them into a mp.matrix
        A = mpm.matrix([
            [ utils.se2mpm(ele, mpm.mp.dps) for ele in row ]
            for row in Asym.tolist()
        ]) 

        # Check if all elements of the matrix have a zero imaginary part
        is_A_real = all(mpm.im(x) == 0 for x in A)
        if is_A_real:
            print('All the elements of the matrix are real')
        else:
            print('The matrix has imaginary complex or imeginary elements.')

        # Calculate the eigenvectors
        with mpm.workdps(decimal_places):
            print(f"decimal_places = {mpm.mp.dps}.")
            values , vectors = mpm.eig( A )
            
        print( 'Number of modes:' , len( values) )

        # Normalize each eigenvector
        for idx in range( vectors.cols ) :
            # The L-infinity norm is the maximum of the absolute values
            vectors[:,idx] = vectors[:,idx] / mpm.norm( vectors[:,idx] , p=mpm.inf)

        
        # Transpose so the eigenvector set becomes a list of lists 
        vectors = vectors.T.tolist()

        # Automatically chops imaginary noise near current precision limits, 
        # and converts mpc(x, 0) into a pure real mpf(x)
        values = [mpm.chop(ev) for ev in values]
        vectors = [mpm.chop(ev) for ev in vectors]

        # Check if all eigenvalues are positive
        if all(item >= 0 for item in values):
            print('All eigenvalues are positive.')
        else:
            print('There are imaginary eigenfrequencies:')
            mpm.nprint(sorted( values, key=lambda z: (z.real, z.imag) ), 6)  

        # Sort eigenvalues and eigenvectors from lowest to highest frequency
        sorted_pairs = sorted( list( zip( values, vectors ) ) )
        
        # Create a nested dictionary to store eigenvector information
        self.eigen_dict = defaultdict(dict)
        for idx , ( val , vec ) in enumerate( sorted_pairs  ):
            if val < 0:
                print(f'Imaginary frequency detected: {idx+1}, { mpm.nstr( mpm.sqrt( val ) / ( 2 * mpm.pi ) , 5 ) }.')
            self.eigen_dict[ idx + 1 ]['frequency'] = mpm.sqrt( mpm.fabs( val ) ) / ( 2 * mpm.pi )  # idx + 1 to begin counting modes from 1
            self.eigen_dict[ idx + 1 ]['vector_dict'] = dict( zip( self.body_coords_list , vec ) )

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Finished, elapsed time: {elapsed_time:.4f} seconds.\nYou can see the eigenfrequency list by calling info.print_eigenfreq({self.name})")

    
    def prepare_transfer_functions( self ):
        """
        """
        if sympify( self.K_eff_matrix ).has(se.I) == False  : # Check whether there's any imaginary unit in the stiffness matrix
            cprint( f"""Warning: it seems that the current value of the stiffness matrix `{self.name}.K_eff_matrix`
            does not accout for structural damping.
            Fix this by calling {self.name}.calculate_stiffness_matrix( with_damping = True ).""" , 'red')

        self.E_matrix = self.K_eff_matrix - self.w**2 * self.M_matrix # Equation of motion matrix; self.w is the angular velocity.
        self.TF_matrix = self.E_matrix.inv() * self.C_XS_eff_matrix   # Transfer function matrix

        # Dictionary to store transfer functions
        # For TFs from ground coordinates to body coordinates
        self.tf_dict = { inc : { outc : None for outc in self.body_coords_list } for inc in self.gnd_coords_list }
        
        # The entries for the TFs from generalized forces to body coordinates still has to be implemented here

    def transfer_function( self , in_coord , out_coord ):
        """
        """
        tf = self.tf_dict[ in_coord ][ out_coord ]
        if tf == None :
            in_idx = self.gnd_coords_list.index( in_coord )
            out_idx = self.body_coords_list.index( out_coord )

            # Lambidify with Sympy to use mpmath
            # In case you need to call this function directly, you need
            # to unpack the argument: grad_lambda( *argument )
            tf = splambdify( [self.w] , self.TF_matrix[ out_idx , in_idx ] , modules='mpmath')  
            
            self.tf_dict[ in_coord ][ out_coord ] = tf # Put the transfer function in a dictionary in case it's requested again

        f_test = 10e-3 # Test frequency, to check whether the TF is zero
        if tf( 2*np.pi * f_test ) == 0 :
            print(f"It seems the output is not coupled to the input, the transfer function is zero at a test frequency of { f_test * 1e3 } mHz.")

        return tf
