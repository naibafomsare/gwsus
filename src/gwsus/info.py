import bigtree as bt
from tabulate import tabulate
from itertools import zip_longest
from math import ceil

VERBOSITY_LEVEL = 1

def vprint(message, level=1, **kwargs):
    '''Print message only when the verbosity level is high enough.'''
    if VERBOSITY_LEVEL >= level:
        print( message , **kwargs)

def show_info(sus, info_set='load'):
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

    print(tabulate( new_dict  , headers="keys", tablefmt="rounded_grid"))
    # print( tabulate( sus.link_table , headers = headers , tablefmt="grid" ,  floatfmt=[ None , ",.3f" , None , ",.3f" , ",.4e" , ",.4e" ] ) )


def print_equilibrium_positions( sus , n_tables = 3 ) :
    # Print the results in table form
    dict_calc = sus.equi_coords_dict
    if dict_calc != None:
        dict_guess = sus.equi_coords_guess_dict
        data = [[str(k), dict_guess[k] , v ] for k, v in dict_calc.items()] # Convert to a list of lists
        headers = ['Symbol', 'Estimated\nvalue [m]', 'Final\nvalue [m]'] 
        tabulate_side_by_side(data, headers, n_tables = n_tables )
    else:
        print("The equilibrium coordinates haven't been calculated, call calculate_equilibrium_positions() to do it.")


def print_eigenfreq( sus , n_tables = 3 ):
    # Print the results in table form
    eigen_dict = sus.eigen_dict
    data = [[ k , v['frequency'] ] for k, v in eigen_dict.items()]
    headers = ['Mode\nnumber', 'Frequency\n[Hz]' ] 
    tabulate_side_by_side(data, headers, n_tables = n_tables )    
        
def print_eigen( sus , mode_num , n_tables = 3 ):
    eigen_dict = sus.eigen_dict
    nn = len( eigen_dict )
    if ( mode_num < 1 ) or ( mode_num > nn ):
        print( "The mode number must be between 1 and" , nn , "inclusive.")
        return                                 
    # print( 'All frequencies [Hz]:' , [ round( item['frequency'],3) for item in sus.eigen_dict.values() ] , '\n')
    print( 'Mode number:' , mode_num , '\n')
    print( 'Frequency:' , round( sus.eigen_dict[ mode_num ]['frequency'] , 3 ) , 'Hz\n' ) 
    data = [[ str(k) , v ] for k, v in eigen_dict[mode_num]['vector_dict'].items()]
    headers = ['Coordinate', 'Value' ] 
    tabulate_side_by_side(data, headers, n_tables=n_tables )
    
    # data = [ {'Coordinate' : coord.name , 'Value' : value}  for ( coord, value ) in sus.eigen_dict[ mode_num ]['vector_dict'].items() ] 
    # print(tabulate( data, headers="keys", tablefmt="grid"))


def tabulate_side_by_side(data, headers, n_tables=1, tablefmt="rounded_grid", spacing=3):
    """
    Split a long table into n_tables smaller tables and print them side by side.

    Parameters
    ----------
    data : list of lists
        The rows of the original table.
    headers : list
        The column headers of the original table.
    n_tables : int
        Number of tables to display side by side.
    tablefmt : str
        Table format supported by tabulate.
    spacing : int
        Number of spaces between tables.
    """
    if n_tables < 1:
        raise ValueError("n_tables must be at least 1")

    if not data:
        print(tabulate([], headers=headers, tablefmt=tablefmt))
        return

    # Determine the number of rows per smaller table
    chunk_size = ceil(len(data) / n_tables)

    # Split the original data into smaller tables
    chunks = [
        data[i:i + chunk_size]
        for i in range(0, len(data), chunk_size)
    ]

    # Format each smaller table independently
    formatted_tables = [
        tabulate(chunk, headers=headers, tablefmt=tablefmt).splitlines()
        for chunk in chunks
    ]

    # Calculate the width of each formatted table
    widths = [
        max(len(line) for line in table)
        for table in formatted_tables
    ]

    # Print the tables side by side
    separator = " " * spacing

    for lines in zip_longest(*formatted_tables, fillvalue=""):
        print(
            separator.join(
                line.ljust(width)
                for line, width in zip(lines, widths)
            ).rstrip()
        )
