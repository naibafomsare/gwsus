import bigtree as bt
from tabulate import tabulate

def show_info( sus , info_set = 'load' ):
    '''
    Introduce the option to use different pre-selected data sets.
    '''
    if sus.root == None:
        print( "Nothing has been connected yet, there's nothing to show." )
        return

    attr_dict = { "mass": "Mass" , "load" : "Load", "link": "Link"}
    root = sus.root
    tree = bt.Tree( root )
    raw_dict = tree.to_dict(name_key="Name", attr_dict=attr_dict ) # Raw dict produced by bigtree
    #print( raw_dict )
    
    new_dict = {}        
    if info_set == 'load':
        new_dict[ "Name" ] = [ value["Name"] for value in raw_dict.values() ] 
        new_dict[ "Mass [kg]" ] = [ value["Mass"] for value in raw_dict.values() ] 
        new_dict[ "Load [kg]" ] = [ value["Load"] for value in raw_dict.values() ] 
        new_dict[ "Number of\nlinks in set" ] = [ value["Link"].num if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        new_dict[ "Single link\nload [kg]" ] = [ value["Link"].load_single if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        
    elif info_set == 'links':
        new_dict[ "Name" ] = [ value["Name"] for value in raw_dict.values() ] 
        new_dict[ "Link set\ntotal load\n[kg]" ] = [ value["Link"].load if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        new_dict[ "Number of\nlinks in set" ] = [ value["Link"].num if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        new_dict[ "Single link\nload [kg]" ] = [ value["Link"].load_single if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        new_dict[ "Axial\nstiffness\n[N/m]" ] = [ value["Link"].k_axial if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        new_dict[ "Torsional\nstiffness\n[Nm/rad]" ] = [ value["Link"].k_torsion if value["Link"] != None else None for value in raw_dict.values() ] # Ground's link is None
        
    else:
        print( "The type of information requested was not understood, the options are: 'load' and 'links'." )
        return

    print(tabulate( new_dict  , headers="keys", tablefmt="grid"))
    # print( tabulate( sus.link_table , headers = headers , tablefmt="grid" ,  floatfmt=[ None , ",.3f" , None , ",.3f" , ",.4e" , ",.4e" ] ) )


def print_equilibrium_positions( sus ) :
    # Print the results in table form
    my_dict = sus.equi_coords_dict
    if my_dict != None:
        guess = sus.equi_coords_guess_dict
        datak = [ {'Symbol' : coord.name , 'Guessed\nvalue' : guess[ coord ] , 'Calculated\nvalue' : value }  for ( coord, value ) in my_dict.items() ]
        print(tabulate( datak, headers="keys", tablefmt="grid"))
    else:
        print("The equilibrium coordinates haven't been calculated, call calculate_equilibrium_positions() to do it.")


def print_eigenfreq( sus ):
    my_dict = { 'Mode\nnumber' : [] , 'Frequency\n[Hz]' : [] }
    for key , item in sus.eigen_dict.items() :
        my_dict[ 'Mode\nnumber' ].append( key )
        my_dict[ 'Frequency\n[Hz]' ].append( round( item['frequency'] , 3 ) )
    print(tabulate( my_dict , headers="keys", tablefmt="grid"))
    
        
def print_eigen( sus , mode_num ):
    
    nn = len( sus.eigen_dict )
    if ( mode_num < 1 ) or ( mode_num > nn ):
        print( "The mode number must be between 1 and" , nn , "inclusive.")
        return                                 
    
    # print( 'All frequencies [Hz]:' , [ round( item['frequency'],3) for item in sus.eigen_dict.values() ] , '\n')
    print( 'Mode number:' , mode_num )
    print( 'Frequency:' , round( sus.eigen_dict[ mode_num ]['frequency'] , 3 ) , 'Hz\n' ) 
    data = [ {'Coordinate' : coord.name , 'Value' : value}  for ( coord, value ) in sus.eigen_dict[ mode_num ]['vector_dict'].items() ] 
    print(tabulate( data, headers="keys", tablefmt="grid"))


