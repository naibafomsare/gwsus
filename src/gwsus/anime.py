import symengine as se
from . import utils
from collections import defaultdict

def prepare_anime( sus ):
    """
    Parameter
    ---------
    sus : gwsus.Suspension
        Suspension
    """
    
    # Symbols
    k , omega , t = se.symbols( 'k \omega t')
    N = len( sus.body_coords_list ) # Number of elements in an eigenvector
    A = se.symbols(f'A0:{N}') # Declares symbols A0,... AN symbols for the eigenverctor elements
    sinwt = se.sin( omega * t )
    
    # Time-dependent values of coordinates 
    equi_dict = sus.equi_coords_dict
    time_dict = sus.gnd0.copy()
    for idx , coord in enumerate( sus.body_coords_list ) : # Eigenvectors are only for body coordinates, not for floats
        time_dict[ coord ] =  equi_dict[ coord ] + k * A[ idx ] * sinwt

    # Calculated in methods:
    # `suspension.calculate_stiffness_matrix`
    # `suspension.create_coords_list`
    dummy_list = sus.float_coords_vector.T.tolist()[0]
    for idx , coord in enumerate( sus.float_coords_list ) :
        time_dict[ coord ] = dummy_list[ idx ].subs( time_dict ) # Because float coordinates are written in terms of body coordinates

    
    for body in sus.body_list[1:] : # Without the ground
        
        #---------- For bodies ---------------#
        pos = body.r.subs( time_dict ).T.tolist()[0] # Position of body

        # print( pos.subs({t:0} ) ) ###########################################################################
        # print( body.name )
        # for item in pos:
        #     print( item.subs({t:0} ).n(10) )
        
        Rot = utils.rotB2S( body ) # Rotation matrix using body's roll, pitch and yaw angles.
        axis = ( ( Rot * se.Matrix( [ 1 , 0 , 0 ] ) ).subs( time_dict ).T ).tolist()[0] # Forward direction of body
        up = ( ( Rot * se.Matrix( [ 0 , 0 , 1 ] ) ).subs( time_dict ).T ).tolist()[0] # Upward direction of body
        orien = [ pos , axis , up ]
        body.orien_lambda = se.lambdify( [ *A , k , omega , t ] , orien )
        
        
        #--------- For links -----------------#
        # Substitute coordinates by time-dependent expressions
        points_exp =  [ item.subs( time_dict ).T.tolist()[0] for item in body.link.r_lower ]
        points_diff_exp =  [ item.subs( time_dict ).T.tolist()[0] for item in body.link.r_diff ]
        
        # Declare the information directly useful for animation
        orienw = [ points_exp , points_diff_exp ]
        body.orienw_lambda = se.lambdify( [ *A , k , omega , t ] , orienw )


def show_anime( sus , mode_num = 1 ):
    '''
    Shows the animation of the eigenmode
    '''
    # The library vpyton is loaded in this method where the canvas is created,
    # so the bahaviour is compatible with Rise in Jupyter
    import vpython as vp  
    
    nn = len( sus.eigen_dict )
    if ( mode_num < 1 ) or ( mode_num > nn ):
        print( "The mode number must be between 1 and" , nn , "inclusive.")
        return

    #------------- Canvas -------------------#
    
    # half of the vertical position of the CM of the lowermost body
    ver_lowest = min( [ float(value) for value in sus.equi_coords_dict.values() ] )
    ver_center = ver_lowest * 1.1 / 2 # Choose a convenient center of the scene
    range_default = abs( ver_lowest ) / 2
    
    # scene = vp.canvas(title=sus.name )
    scene = vp.canvas()
    # scene.waitfor('paint')
    # scene.background = vp.vec( 0 , 0 , 0 ) # Completely black background
    # scene.background = vp.vec(17/255,17/255,17/255) # Background color in Jupyterlab output cell
    scene.background = vp.vec(13/255,17/255,23/255) # Background color in Jupyterlab output cell
    scene.autoscale = False
    sc = 0.95 ; scene.width = sc*480 ; scene.height = sc*640
    scene.center = vp.vec( 0 , 0 , ver_center )
    scene.up = vp.vec( 0 , 0 , 1 ) ; scene.forward = vp.vec(-1,-1,-1)
    scene.range = range_default
    
    # --- Control buttons --- #

    state = {'running': False , 'break' : False}
    
    def start_pause_button(b):
        state['running'] = not state['running']
        if state['running']: # running:
            b.text = "Pause"
        else:
            b.text = "Run"
    
    def delete_the_canvas(b):
        # scene.delete() ; # scene.title = ""
        pause_button.delete() ; delete_button.delete() ; reset_view_button.delete()
        side_view_button.delete() ; top_view_button.delete() ; front_view_button.delete()
        # autoscale_button.delete()
        state['break'] = not state['break']
        scene.delete()
        # print('Animation finished.')
        # You can add other actions here if needed, like creating a new canvas   
    
    def reset_view():
        scene.center = vp.vec( 0 , 0 , ver_center )
        scene.up = vp.vec(0,0,1) ; scene.forward = vp.vec(-1,-1,-1)
        scene.range = range_default

    def front_view():
        scene.camera.pos = vp.vec( 0.4 , 0 , ver_center) # Position camera
        scene.up = vp.vec(0,0,1)
        scene.camera.axis = - scene.camera.pos + vp.vec( 0 , 0 , ver_center )
        scene.range = range_default
        
    def side_view():
        scene.camera.pos = vp.vec( 0, 0.4, ver_center ) # Position camera
        scene.up = vp.vec(0,0,1)
        scene.camera.axis = - scene.camera.pos + vp.vec( 0 , 0 , ver_center )
        scene.range = range_default
        
           
    def top_view():
        scene.camera.pos = vp.vec(0, 0, 0.1 ) # Position camera
        scene.up = vp.vec(1,0,0)
        scene.camera.axis = - scene.camera.pos + vp.vec( 0 , 0 , ver_center )
        scene.range = range_default 
         
    # def autoscale(b):
    #     scene.autoscale = not scene.autoscale
    #     if scene.autoscale:
    #         b.text = "Autoscale on"
    #     else:
    #         b.text = "Autoscale off"
                               
    # The 'b' argument is automatically passed to the function when clicked.
    pause_button = vp.button(bind=start_pause_button, text='Run', pos=scene.caption_anchor)
    reset_view_button =vp.button(bind=reset_view, text='Reset view')
    front_view_button =vp.button(bind=front_view, text='Front view')
    side_view_button =vp.button(bind=side_view, text='Side view')
    top_view_button =vp.button(bind=top_view, text='Top view')
    # autoscale_button =vp.button(bind=autoscale, text='Autoscale off')
    scene.append_to_caption('\n\n')
    delete_button = vp.button(text="Delete Canvas", bind=delete_the_canvas , pos=scene.caption_anchor )
    
    #------ Draw bodies in the equilibrium position -----#
            
    # Retrieve the information about the mode shape
    mode_dict = sus.eigen_dict[ mode_num ]['vector_dict']
    An = [ None ] * len( mode_dict )
    for idx , coord in enumerate( sus.body_coords_list ) :
        An[ idx ] = mode_dict[ coord ]
        
    k = 0.3       # amplitude adjustment factor
    omega = 10    # Angular frequency (determines speed of oscillation)
    t = 0         # Initial time
    dt = 0.01     # Time step
    
    # Draw bodies and links when they are wires.
    cyl_dict = defaultdict(dict)
    for idxi , body in enumerate( sus.body_list[1:] ) :
        [ posi , axisi , upi ] = body.orien_lambda( *An , k , omega , t ) ############################################ Without * for Sympy
        body.shape_instance = body.shape( cm_pos = posi , axis = axisi , up = upi ) # Create and draw 3D bodies

        # print( body.shape_instance.shape.size ) # Dimensions of the box surrounding the object
        
        [ posiw , axisiw ] = body.orienw_lambda( *An , k , omega , t ) ################################################################# Without * for Sympy
        for idxj , ( pos , axis ) in enumerate( zip( posiw , axisiw ) ):
            params_dict = body.link.shape_parameters() # Retrieve additional shape parameters
            cyl_dict[idxi][idxj] = body.link.shape( pos=pos , axis=axis , **params_dict) # Create and draw links
            
    #------ Animate -------#
            
    while True:
        vp.rate( 24 )
         
        if not state['break']:
            if state['running']: 
                for idxi , body in enumerate( sus.body_list[1:] ) :
                    [ pos , axis , up ] = body.orien_lambda( *An , k , omega , t ) ############################# Without * for Sympy
                    body.shape_instance.update_pos( pos , axis , up ) # Update 3D bodies
                    
                    [ posw , axisw ] = body.orienw_lambda( *An , k , omega , t ) ################################################## Without * for Sympy
                    for idxj , ( pos , axis ) in enumerate( zip( posw , axisw ) ):
                        cyl_dict[idxi][idxj].update_pos( pos , axis ) # Update links
                    
                t = t + dt
        else: break
