import symengine as se
import mpmath as mpm # in pendulum_toolkit()
from fractions import Fraction as frac
import numpy as np
# from types import SimpleNamespace
# from sympy import sympify # for commented function show_matrices()
import sympy as sp
from sympy import mathematica_code as mcode


def con( *args ):
    """
    Convert input to Symengine rationals.

    Parameters
    ----------
    *args
        It could either be a float, an int, a number of floats or ints,
        or a tuple or list of floats or ints.

    Returns
    -------
    se.Rational or tuple[se.Rational]
        Depending on the input, it could either return a Symegine
        rational or a tuple of Symengine rationals.   
    """
    if isinstance(args[0], (list, tuple)): args = args[0] 
    data = tuple( map( lambda x: se.Rational( frac(x).numerator, frac(x).denominator) , args ) )
    return data if len(data) > 1 else data[0] if data else None

def rectangle( l , t , ver ):
    '''
    Generate a list of position vectors laid out in the vertices
    of a rectangle, whose sides are aligned with the longitudinal
    and transverse directions. In other words, the plane is parallel 
    to the longitudinal-transverse plane. The rectangle is centered
    at the center of mass when seen from above, and displaced from
    it vertically when seen from the side.
    
    Parameters
    ----------
    l: float
        Wire separation in the longitudinal direction.
    t: float
        Wire separation in the transverse direction.
    ver: float
        Position of the plane w.r.t. the center of mass.

    Returns
    -------
    list
        List of four Symengine column position vectors, listed counterclockwise from the positive longitudinal direction.
    '''
    # floats are converted to rationals with con() and unpacked with *
    r = se.Matrix( [ * con( l , t , ver ) ] ) 

    # The position vactors are produced.
    # Regular ints multiplied by Symenagine rationals always produce Symengine objects.
    return [ se.diag( a * half , b * half , 1 ) * r  for a , b in zip( [1,-1,-1,1] , [1,1,-1,-1] ) ]

def triangle( pcd , ver , direction = '+L' ):
    '''
    Generate a list of position vectors laid out in the vertices
    of an equlateral triangle. The plane of the triangle is parallel 
    to the longitudinal-transverse plane. It is centered
    at the center of mass when seen from above, and displaced from
    it vertically when seen from the side.
    
    Parameters
    ----------
    pcd: float
        Pitch circle diameter.
    ver: float
        Position of the plane w.r.t. the center of mass.
    direction: str
        Direction one of the tips of the triangle
        points to. It can either point to the positive
        (``'+L'``) or negative (``'-L'``) longitudinal directions. 

    Returns
    -------
    list
        List of three Symengine column position vectors, listed counterclockwise from the positive longitudinal direction.
    '''
    pcr = half * con( pcd )
    ver = con( ver )
    if direction == '+L':
        vec = se.Matrix( [ pcr , 0 , ver ] )
    elif direction == '-L':
        vec = se.Matrix( [ pcr * se.cos( se.pi * se.Rational(60, 180)  ) , pcr * se.sin( se.pi * se.Rational(60, 180) ) , ver ] )
    else:
        print("Unrecognized orientation, the only options are '+L' and '-L'.")
        return
    return [ rot_yaw_S2B( -se.pi * se.Rational(gamma, 180) ) * vec for gamma in [ 0 , 120 , 240 ] ]


g = con( 9.80665 ) # gravity acceleration in m/s**2

half = con(1/2)

def matrix_3x3( list_matrix: list[ list[ float ] ] ):
    '''
    Create a 3×3 Symengine matrix
    whose elements are rationals.

    Parameters
    ----------
    list_matrix : list[ list[ float ] ]
        Matrix as a list of sublists of floats,
        with each sublist representing a row.

    Returns
    -------
    se.Matrix
        Symengine matrix of rational numbers.        
    '''
    return se.Matrix( [ [ *con( list_matrix[0] ) ],
                        [ *con( list_matrix[1] ) ],
                        [ *con( list_matrix[2] ) ] ] )
    

def matrix_3x3_diagonal( ele1 , ele2 , ele3 ):
    '''
    Create a 3×3 Symengine diagonal matrix
    whose elements are rationals.

    Parameters
    ----------
    ele1, ele2, ele3 : float
        Element in the diagonal of the matrix. 

    Returns
    -------
    se.Matrix
        Symengine diagonal matrix of rational numbers.        
    '''
    return se.diag( *con( ele1 , ele2 , ele3 ) )

func_list = [ sp.cancel , sp.factor , sp.simplify ]
def simplify( term , subs_dict ):
    simp = term
    for func in func_list:
        simp = func( simp )
        simp_num = simp.subs( subs_dict )
        if not simp_num.has( sp.nan ): # As soon as it is not nan
            return simp_num            # Returns the value
    return simp_num # When out of options, return nan. 

def cancel_nan(symbol, expr, subs_dict):
    '''
    This is text
    '''
    # Creates a copy of the original dict so it's not modified
    filter_dict = subs_dict.copy()

    # Removes from the dict the symbol that produces the Nan
    filter_dict.pop(symbol)
    term = sp.simplify(expr.subs(filter_dict))

    # Creates a non negative symbol to keep sp.cancel()
    # from generating an error
    x = sp.symbols('x', nonnegative=True)
    term = term.subs({symbol: x})

    # Eliminate the specific symbol
    term = sp.cancel(term, x)

    # Substitute the original problematic numeric value, typically zero.
    return term.subs({x: subs_dict[symbol]})

def se2mpm( number , prec ):
    '''
    Convert number from Symengine to Mpmath
    '''
    number = number.n(prec)
    number_mpc = mpm.mpc( str(number.real), str(number.imag) ) 
    return mpm.chop( number_mpc )

'''
Passive rotation matrices: transform body to space coordinates (B2S).
'''

def rot_roll_S2B( alpha ):
    """ 
    Returns a passive rotation matrix for **roll**, i.e, for a rotation around the **longitudinal axis.**

    Parameter
    ---------
    alpha : various types
        Rotation angle measured in radians.

    Returns
    -------
    symengine.DenseMatrix
    """  
    return se.Matrix( [ [ 1 , 0 , 0 ] , [ 0 , se.cos( alpha ) , se.sin( alpha )  ] , [0 , -se.sin( alpha ) , se.cos( alpha ) ] ] )

def rot_pitch_S2B( beta ):
    """ 
    Returns a passive rotation matrix for **pitch**, i.e, for a rotation around the **transverse axis.**

    Parameter
    ---------
    beta : various types
        Rotation angle measured in radians
    """
    return se.Matrix( [ [ se.cos( beta ) , 0 , -se.sin( beta ) ] , [ 0 , 1 , 0 ] , [ se.sin( beta ) , 0 , se.cos( beta )  ]  ] )

def rot_yaw_S2B( gamma ):
    """ 
    Returns a passive rotation matrix for **yaw**, i.e, for a rotation around the vertical axis.

    Parameter
    ---------
    gamma : various types
        Rotation angle measured in radians
    """
    return se.Matrix( [ [ se.cos( gamma ) , se.sin( gamma ) , 0 ] , [ -se.sin( gamma ) , se.cos( gamma ) , 0 ] , [ 0 , 0 , 1 ] ] )


def rotS2B_byangle( roll , pitch , yaw ):
    """
    Rotation matrix for a ... , passive rotation transforming
    from space to body coordinates in this order: yaw --> pitch --> roll.

    Parameters
    ----------
    roll : various types
        Rotation angle around the longitudinal axis, measured in radians.
    pitch : various types
        Rotation angle around the transverse axis, measured in radians.
    yaw : various types
        Rotation angle around the vertical axis, measured in radians.
    """
    return rot_roll_S2B( roll ) @ rot_pitch_S2B( pitch ) @ rot_yaw_S2B( yaw )


def rotS2B( body ):
    """
    """
    return rotS2B_byangle( body.roll , body.pitch , body.yaw )


def rotB2S( body ):
    '''
    The inverse of rotS2B
    '''
    return rotS2B( body ).T

# def show_matrices():
    # roll , pitch , yaw  = se.symbols('roll pitch yaw')
    # display( sympify( rotlS2B( roll ) ) )
    # display( sympify( rottS2B( pitch ) ) )
    # display( sympify( rotvS2B( yaw ) ) )
    # display( 'rot_B2S = ' , sympify( rotB2S( roll , pitch , yaw ) ) )
    # display( 'rot_S2B = ' , sympify( rotS2B( roll , pitch , yaw ) ) )

def kk_series( k ):
    '''
    k is a numpy array with the spring constants of the individual springs.
    '''
    return 1 / np.sum( 1 / k )


def center( ver ):
    """
    Returns a list with the position vector of an attachment point at the geometric coordinates 
    """
    # return [ se.Matrix( [  0 , 0 , con( ver ) ] ) ]
    return [ se.Matrix( [  *con( 0 ,  0 , ver ) ] ) ]





def chop(array, tolerance=1e-10):
    """
    Replaces elements in a numpy array with 0 if their absolute magnitude 
    is below the specified tolerance.
    """
    chopped_array = array.copy() # Avoid modifying the original array in place
    chopped_array[np.abs(chopped_array) < tolerance] = 0
    return chopped_array
    
#-------------------- Generate pendulum toolkit file ------------------------------------#

def pendulum_toolkit( sus , path , file_name ):
    """
    Generates a file with the definition of the model for use in Pendulum Toolkit.

    Parameters
    ----------
    sus : gwsus.suspension
        Suspension whose specifications will be written in the file.
    path : string
        Path to the directory where the file will be saved, e.g., 'my/mathematica/directory/'.
    file_name : string
        By convention, the name of the file will be file_name + 'Defn.m', e.g., 'myModelDefn.m'.
    """
    
    model_name = sus.name
    model_version = 6.0
    model_comment = "This is a comment about the model."
    
    load_libraries = """(* ::Input::Initialization:: *)
Off[General::spell,General::spell1]

(* ::Input::Initialization:: *)
doplots=True;

(* ::Input::Initialization:: *)
doplots::usage="doplots is a switch that enables plotting when set to True";

(* ::Input::Initialization:: *)
If[$VersionNumber<6.,Needs["Graphics`Graphics`"]]

(* ::Input::Initialization:: *)
If[$VersionNumber<6.,Needs["Graphics`Shapes`"]];

(* ::Input::Initialization:: *)
If[$VersionNumber<6.,Needs["Graphics`Polyhedra`"]]

(* ::Input::Initialization:: *)
If[$VersionNumber<6,Needs["LinearAlgebra`MatrixManipulation`"]]
    
(* ::Input::Initialization:: *)
Needs["RotationsXYZ`"]

(* ::Input::Initialization:: *)
Needs["StatusWindow`"];

(* ::Input::Initialization:: *)
Needs["MatlabExport`"];

(* ::Input::Initialization:: *)
Needs["IFOModel`"];

(* ::Input::Initialization:: *)
Needs["PendUtil`"];

(* ::Input::Initialization:: *)
If[utilitiesversion>=5.0,
Null,
Print["Incorrect utilities version"];Abort[],
Print["Utilities failed to load"];Abort[]
]; """
    
    # allvars (body coordinates)
    my_list = sus.body_coords_list
    all_vars = mcode( [ item.name for item in my_list ] )
    
    # allfloats
    my_list = sus.float_coords_list
    all_floats = mcode( [ item.name for item in my_list ] )
    
    # allparams (ground coordinates)
    my_list = sus.gnd_coords_list
    all_params = mcode( [ item.name for item in my_list ] )
    non_opt_coords = all_params 
    
    # Coordinate lists by body
    coords_by_body = ""
    for body in sus.body_list: # Include ground
        coords_list = mcode( [ body.lon.name , body.tra.name , body.ver.name , body.yaw.name , body.pitch.name , body.roll.name ] )
        coords_by_body = coords_by_body + f"{ body.name } =" + coords_list + '\n'
    
    body_origin = """LOC = {0,0,0} ;
    COM = LOC ;
    FRP = LOC ;"""
    
    # gravlist, gravitational potential energy
    my_list = sus.body_list[1:] # The ground is excluded
    grav_list = mcode( [ f"m{body.name} * g * {body.ver}" for body in my_list ] )
    
    nl = ",\n"
    nl2 = ",\n\n"

    # Wires
    wire_list = []
    for body in sus.body_list[1:] : # Ground excluded
        for idx in range(body.link.num):
            my_list_1 = body.parent.attachment_points_p[body.link.point_name_upper][idx].T.tolist()[0] # Attachment point coordinate values
            my_list_2 = body.attachment_points_p[body.link.point_name][idx].T.tolist()[0] # Attachment point coordinate values
            my_list_3 = [
            # Upper body
            mcode( [ body.parent.lon , body.parent.tra , body.parent.ver , body.parent.yaw , body.parent.pitch , body.parent.roll ] ),
            mcode( [item.evalf() for item in my_list_1] ) , # Evaluate numerically element-wise and convert to Mathematica
            mcode( [ 0 , 0 , -1 ] ),
            # Lower body
            mcode( [ body.lon , body.tra , body.ver , body.yaw , body.pitch , body.roll ] ) ,
            mcode( [ item.evalf() for item in my_list_2 ] ) , # Evaluate numerically element-wise and convert to Mathematica
            [ 0 , 0 , 1 ] ,
            body.link.material.young_modulus ,
            body.link.ll.sum().evalf() , # ", (* unstretched length *)"
            body.link.k_axial.evalf() , # ", (* longitudinal elasticity *)" ,
            [ 1 , 0 , 0 ] , # ", (* vector defining principal axis 1 *)" ,
            body.link.JJ[0].evalf() , # ", (* moment of area along principal axis 1 *)" ,
            body.link.JJ[0].evalf() , # ", (* moment of area along principal axis 2 *)" ,
            "nodamp" , # "(* linear elasticity type *)" ,
            "nodamp" , # "(* angular elasticity type *)" ,
            "nodamp" , # "(* torsional elasticity type *)" ,
            body.link.material.shear_modulus.evalf() , # ", (* shear modulus *)" ,
            body.link.AA[0].evalf() , # ", (* cross sectional area for torsional calculations *)" ,
            body.link.JJee[0].evalf()  # "(* torsional stiffness geometric factor *)" 
            ]
            wire_list.append( f'{{{nl.join(map(str, my_list_3 ))} }}' ) # Convert to string and join with '\n' for clarity in the exported file
    
    # Moments of inertia
    my_list = sus.body_list[1:] # Without the ground
    dummy = ( f"moi{body.name} = {mcode(body.moi)} ; \n" for body in my_list ) 
    moi = f"{''.join( dummy)}"

    # kinetic
    my_list = sus.body_list[1:] # Without the ground
    dummy = [ ( f"+(1/2)*m{body.name}*Plus@@(Dt[b2s[{body.name},COM],t]^2)"
                f" + (1/2)*omegaB[{body.yaw}, {body.pitch}, {body.roll}].moi{body.name}.omegaB[{body.yaw}, {body.pitch}, {body.roll}]\n")
              for body in my_list ]
    kinetic = f"(\n{''.join( dummy)} ) ;"
    
    # defaultvalues
    my_list = sus.body_list[1:]
    dummy = [ f"m{body.name} -> {body.mass}" for body in my_list ] # body masses
    dummy = dummy + [f"g -> {g}", "temperature -> 298" , "boltzmann -> 1.380649*^-23" , "damping[real,nodamp] -> (1&)" , "damping[imag,nodamp] -> (0&)" , "constraintsubstitutions[]"] 
    default_values = f"{{ {', '.join( dummy)} }} ;"
    
    # startpos
    my_dict = sus.equi_coords_guess_dict
    start_pos = mcode( { key : value.n( mpm.mp.dps ) for key , value in my_dict.items() } ).replace(':',' ->')

    suspension_definition = f"""
(* File generated with gwsus *)

modelname = {model_name}
modelversion = {model_version}
modelcomment = {model_comment}

{load_libraries}

(* Body coordinates *)
allvars = {all_vars}
    
(* Float coordinates *)
allfloats = {all_floats}

(* Ground coordinates *)
allparams = {all_params}

(* Coordinates to be considered fixed for the purposes of finding the equililibrium position *)
nonoptcoords = {non_opt_coords}

(* Coordinate lists by body, elements are in prescribed order *)
{coords_by_body}

(* Origin of local coordinate systems *)
{body_origin}

(* Gravitational potential energy *)
gravlist = {grav_list}

wirelist = {{ 
{nl2.join( wire_list )}
}} ;

(* Moments of inertia *)
{moi}

(* Kinetic energy *)
kinetic = {kinetic}

(* Default values of quantities *))
defaultvalues = {default_values}

(* Guessed values of the equilibrium position coordinates *)
startpos = {start_pos}
    """
    
    # Open the file in 'w' (write) mode. This will create a new file or overwrite an existing one.
    with open( path + file_name + "Defn.m" , 'w') as f:
        print( suspension_definition , file=f)

#-----------------------------------------------------------#

from IPython.display import HTML, display

def big_text(text, size = 30 ):
    size = str( size ) + "px"
    display(HTML( f'<span style="font-size: {size};">{text}</span>' ))

def title( text , size = 30 ):
    size = str( size ) + "px"
    display( HTML(
        f'<div style="font-size: {size}; margin-top: 50px; margin-bottom: 15px; color: LightBlue;" > {text} </div>' ) )

def title2( text , size = 30 ):
    size = str( size ) + "px"
    display( HTML(
        f'<div style="font-size: {size}; margin-top: 50px; margin-bottom: 15px; color: white" > {text} </div>' ) )
        # f'<div style="font-size: {size}; margin-top: 50px; margin-bottom: 15px; color: white ; font-weight: bold" > {text} </div>' ) )
