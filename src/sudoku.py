# sudoko.py
"""
This is a program to solve, and someday create, Sudoku puzzles
It was adapted from the Perl program sudoku.pl
To ease the adaption process the original variable, function and file names, where possible, have been preserved.
The Trace.pm module use has been replaced by the select_trace.py module.
""" 


##############
## External ##
##############
from math import *
import datetime
import traceback
import time
import os
import argparse
import re
from tkinter import *




###############
## Libraries ##
###############
from select_trace import SlTrace
from select_error import SelectError
base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
SlTrace.setLogName(base_name)
SlTrace.lg(f"{base_name} {' '.join(sys.argv[1:])}")

from select_window import SelectWindow
from select_control import SelectControl
from variable_control import VariableControl
from trace_control import TraceControl
from tkMath import tkMath

from sudoku_subs import *
import sudoku_globals as g
g.initialize_globals()
##################
## User-defined ##
##################
# Set up main board
def prime_exit():
    SlTrace.lg("Prime Exit")
    g.running = False
    pgm_exit()
    
mw = g.Display_mw = Tk()                 # To support grid layout - MUST be done before wm
mw.title("Sudoku Playing")
mw.protocol("WM_DELETE_WINDOW", prime_exit)
tkMath.setup(mw)
cF = SelectControl(control_prefix="run_control", update_report=update_report)
cF.make_label("Puzzle Dimensions")
g.nCol = cF.make_val("nCol", 9)
g.nSubCol =cF.make_val("nSubCol", 3)
g.nRow = cF.make_val("nRow", 9)
g.nSubRow = cF.make_val("nSubRow", 3)

cF.make_label("Puzzle Size")
g.bSize = cF.make_val("bSize", 3)          # Main Bd size inches
g.sSize = cF.make_val("sSize", 2)          # Solution Bd size
g.nFirst = cF.make_val("nFirst", 5)         # first n solutions
g.makePuzzle = cF.make_val("makePuzzle", False)         # If defined, generate puzzle with this many cells filled
g.makePuzzleSym = cF.make_val("PuzzleSym", "c")      # Puzzle symetry pref for initial settings
                        # x, y, center, n - none
g.traceList = cF.make_val("traceList", "")
g.UsePuzzle = cF.make_val("UsePuzzle", False)
g.xPer = cF.make_val("xPer", False)      # experimental

cF.make_label("Running Control")
g.run_after_load = cF.make_val("run_after_load", False)
                        # Progress display variables
cF.make_label("Display Time")
g.Display_time = cF.make_val("Display_time", .5)            # Display time, None - no display
                        #               0 - wait for continue
                        #               > 0 delay (sec)
g.update_time = cF.make_val("update_time", 10.)
g.Display_board = None
g.Display_prev_time = 0  # Previous display time  
##################
## Main program ##
##################
parser = argparse.ArgumentParser()

###parser.add_argument('--closed_tours', type=str2bool, dest='closed_tours', default=closed_tours)
###parser.add_argument('--display_complete', type=str2bool, dest='display_complete', default=display_complete)
###parser.add_argument('--display_path_board', type=str2bool, dest='display_path_board', default=display_path_board)
###parser.add_argument('--max_look_ahead=', type=int, dest='max_look_ahead', default=max_look_ahead)

parser.add_argument('--cols', type=int, dest='nCol', default=g.nCol)                  # Number of cell col
parser.add_argument('--bSize', type=float, dest='bSize', default=g.bSize)                     # Board size in inches
parser.add_argument('--displayTime', type=float, dest='Display_time', default=g.Display_time)  # Solution step display time (sec)
                                        # 0 - till user ACK, None - none
parser.add_argument('--first', type=int, dest='nFirst', default=g.nFirst)                     # first(atleast) solutions
parser.add_argument('--gcols', type=int, dest='nSubCol', default=g.nSubCol)               # Number of cell col in group
parser.add_argument('--grows=', type=int, dest='nSubRow', default=g.nSubRow)                # Number of cell row in group
parser.add_argument('--makePuzzle', type=int, dest='makePuzzle', default=g.makePuzzle)        # Make random puzzle with n start
parser.add_argument('--msymetric', type=str, dest='makePuzzleSym', default=g.makePuzzleSym)   # Make puzzle symetry
parser.add_argument('--rows', type=int, dest='nRow', default=g.nRow)                  # Number of cell row
parser.add_argument('--run_after_load', type=str2bool, dest='run_after_load', default=g.run_after_load)        # Use preset puzzle
parser.add_argument('--sSize=f', type=float, dest='sSize', default=g.sSize)                   # Solution board size
parser.add_argument('--traceList=s', type=str, dest='traceList', default=g.traceList)         # Comma separated trace list
parser.add_argument('--uPuzzle', type=str2bool, dest='UsePuzzle', default=g.UsePuzzle)        # Use preset puzzle
parser.add_argument('--update_time', type=str2bool, dest='update_time', default=g.update_time)        # Use preset puzzle
parser.add_argument('--xper=n', type=int, dest='xPer', default=g.xPer)                        # Experimental = 1

args = parser.parse_args()             # or raise SelectError("Illegal options")
SlTrace.lg(f"args: {args}")
g.nCol = args.nCol
g.bSize = args.bSize 
g.Display_time = args.Display_time
g.nFirst = args.nFirst
g.nSubCol = args.nSubCol
g.makePuzzle = args.makePuzzle
g.makePuzzleSym = args.makePuzzleSym
g.nRow = args.nRow
g.run_after_load = args.run_after_load
g.sSize = args.sSize
g.traceList = args.traceList
g.UsePuzzle = args.UsePuzzle
g.xPer = args.xPer

                                    # Update persistent values
cF.set_val("bSize", g.bSize)          # Main Bd size inches
cF.set_val("sSize", g.sSize)          # Solution Bd size
cF.set_val("nFirst", g.nFirst)         # first n solutions
cF.set_val("makePuzzle", g.makePuzzle)         # If defined, generate puzzle with this many cells filled
cF.set_val("PuzzleSym", g.makePuzzleSym)      # Puzzle symetry pref for initial settings
                        # x, y, center, n - none
cF.set_val("nCol", g.nCol)
cF.set_val("nSubCol", g.nSubCol)
cF.set_val("nRow", g.nRow)
cF.set_val("nSubRow", g.nSubRow)
cF.set_val("traceList", g.traceList)
cF.set_val("update_time", g.update_time)
cF.set_val("UsePuzzle", g.UsePuzzle)
cF.set_val("xPer", g.xPer)      # experimental
cF.set_val("Display_time", g.Display_time)



trace = True if g.traceList is not None and g.traceList != "" else False
if trace:
    SlTrace.setFlags(g.traceList)

if g.nSubCol is None:
    nSubCol = int(sqrt(g.nCol))
if g.nRow is None:
    g.nRow = g.nCol # Set square by default
if g.nSubRow is None:
    nSubRow = int(sqrt(g.nRow))
makePuzzle = int(g.nCol*g.nRow/3)
if g.makePuzzle % 2 == 1:
    makePuzzle -= 1         # Make even
    
mw.update()
bs_in = int(tkMath.inchesToPixels(g.bSize))
w = bs_in + 200
h = bs_in + 100

    
g.nSol = None                 # Solution window number

g.top_fr = Frame(mw)
g.top_fr.pack(side = 'top')
control_fr = Frame(g.top_fr)
control_fr.pack(side = 'top')
app = SelectWindow(g.Display_mw,
                title="Playing Sudoku",
                arrange_selection=False,
                pgmExit=prime_exit,
                file_open = file_open,
                )
app.add_menu_command("Puzzle", file_open)       # Dedicated puzzle menu item
app.add_menu_command("Contols", set_controls)   # Display variable controls
mw.geometry(f"{w}x{h}")
mw.update()

solve_puzzle = Button(control_fr, 
        text = "Solve Puzzle",               # Guess all remaining
        command = solve_main_puzzle,
        )
solve_puzzle.pack(side = 'left')

make_puzzle_b = Button(control_fr, 
        text = "Make Puzzle",
        command = make_puzzle,
        )
make_puzzle_b.pack(side = 'left')

reset_b = Button(control_fr, 
        text = "Reset",               # Reset to initial setting
        command = reset_board
        )
reset_b.pack(side = 'left')

clear_b = Button(control_fr, 
        text = "Clear Board",
        command = clear_board,
        )
clear_b.pack(side = 'left')





sbox_fr = None                                # Set value frame
sbox = None                                   # selection box
sbox_row = None                               # selected cell row
sbox_col = None
sbox_legal_vals = []                        # legal vals in selection box                                 

g.o_data = None                # Primary data
g.o_board = None               # Primary board
Initial_data = None          # Initial data values

# setup initial position
if g.UsePuzzle:
    use_puzzle()                # Use premade puzzle
else:
    sols = make_puzzle(g.makePuzzle)


                            # Display progress during puzzle solution
  
mw.mainloop()

