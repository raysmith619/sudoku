# sudoku_globals.py
""" Program Globals
We might restucture the program to avoid this at a later date
but to push ahead with most of the structure intqct we have these global variables
"""
from resource_group import ResourceGroup

def initialize_globals():
    global res_group
    global Display_time, Display_prev_time, DisplayRtn, Display_mw, Display_board
    global nRow, nSubRow, nCol, nSubCol, si, sbox_fr, sbox, sbox_row, sbox_col, sbox_legal_vals
    global o_data, o_board, Initial_data, bSize, sSize, nFirst, makePuzzle, makePuzzleSym
    global traceList, UsePuzzle
    global top_bd_fr

    res_group = ResourceGroup()
    Display_time = None
    Display_prev_time = None  # Previous display time
    DisplayRtn = None
    Display_mw = None
    Display_board = None
    nRow = 9         #   number of rows down the whole board
    nSubRow = 3      # number of row cells in sub square
    nCol = 9         # number of cols accross the whole board
    nSubCol = 3      # number of col cells
    
    si = 0                                       # Selection index
    sbox_fr = None                                # Set value frame
    sbox = None                                   # selection box
    sbox_row = None                               # selected cell row
    sbox_col = None
    sbox_legal_vals = []                        # legal vals in selection box                                 
    
    o_data = None                # Primary data
    o_board = None               # Primary board
    Initial_data = None          # Initial data values
    
    bSize = 3          # Main Bd size inches
    sSize = 2          # Solution Bd size
    nFirst = 5         # first n solutions
    makePuzzle = None         # If defined, generate puzzle with this many cells filled
    makePuzzleSym = "c"      # Puzzle symetry pref for initial settings
    traceList = ""
    top_bd_fr = None       # top display frame

if __name__ == "__main__":
    tg = True
    ###tg = False
    if tg:
        import sudoku_globals as g
        g.initialize_globals()
        print(f"nRow={g.nRow} nCol={g.nCol}")
        print(f"Display_mw={g.Display_mw}")
        print(f"o_data={g.o_data}")
    else:
        from sudoku_globals import initialize_globals, nRow, nCol, Display_mw, o_data
        initialize_globals()
        print(f"nRow={nRow} nCol={nCol}")
        print(f"Display_mw={Display_mw}")
        print(f"o_data={o_data}")

   
    
    