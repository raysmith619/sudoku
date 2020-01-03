# sudoku_subs.py
# Top level subs for sudoku.py
# imported to workaround the lack of forward referencing subroutines
import sys
from tkinter import filedialog
from tkinter import *
import time
import argparse
from math import *
from select_trace import SlTrace
from select_error import SelectError
from resource_group import ResourceEntry

import sudoku_globals as g
from SudokuData import SudokuData, CellDesc
from SudokuPuzzle import SudokuPuzzle
from SudokuBoard import SudokuBoard
from SudokuPly import SudokuPly
from sudoku_puzzle_load import SudokuPuzzleLoad


def helpstr():
  retstr = f"""
    --cols number_of_cols Default: {g.nCol}
    --bSize bd size in inches Default: {g.bSize}
    --dispalyTime sec between display, 0 - wait till user ACK
    --first number_of_solutions, stop when we have this many Default: {g.nFirst}
    --makePuzzle starting_cells, make puzzle with this many filled cells
    --gcols number_of_cells_in_group Default: {g.nSubCol}
    --grows number_of_cells_in_group Default: {g.nrowGroup}
    --rows number_of_rows Default: {g.nRow}
    --sSize solution bd size inches Default: {g.sSize}
    --traceList comma_separated_trace_options Default: {g.traceList}
    --uPuzzle - use preformed puzzle
    --xperimental experimental version Default: {g.xPer}
    """

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def pgm_exit():
    SlTrace.lg("Quitting Sudoku Playing")
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    SlTrace.runningJob = False
    g.res_group.destroy_all()
    g.Display_mw.destroy()
    sys.exit(0)

def update():
    """ do any window updating required
    """
    if not SlTrace.runningJob:
        return
    
    if g.Display_mw is not None:
        g.Display_mw.update()                                                                                                                                                                

def set_puzzle(puzzle):
    """ Set/Reset main puzzle
    :puzzle: Puzzle to setup
    """
    display_close()
    if g.o_data is not None:
        g.o_data.clear()
    g.Initial_data = g.o_data  = puzzle.copy()
    if g.o_board is None:
        g.o_board = SudokuBoard(mw=g.Display_mw,
            frame=new_main_bd_frame(),
            data=puzzle,
            bdWidth=g.bSize,
            bdHeight=g.bSize)
 
    g.o_board.showData()
 
#
def use_puzzle(puzzle=None):
    """ Use Precreated puzzle
    Set reset_data to this
                # Pattern
                    Default: PZ1
                    n x n lines
                     - or numeric contents
    """
    ###global g.o_data, g.nCol, g.nSubCol, g.nRow, g.nrowGroup, g.o_board, g.Initial_data, g.nRow, g.nCol
    
# Test puzzles 
    PZ1 = """
        -    2    -    -
        1    4    -    -
        -    -    3    2
        -    -    1    -
    """
    
    PZ2 = """
        3    2    4    1
        1    4    2    3
        4    1    3    2
        2    3    1    4
    """
    
    PZ3 = """
        -    2    4    1
        1    4    2    3
        4    1    3    2
        2    3    1    4
    """
    
    PZ4 = """
        -    -    4    1
        1    4    2    3
        4    1    3    2
        2    3    1    4
    """
    
    
    if puzzle is None:
        puzzle = PZ1
        puzzle = PZ2
        puzzle = PZ3
        puzzle = PZ4
        puzzle = PZ1
    nrow = 0
    ncol = 0
    rowcols = []            # array of rows of cols
    lines = puzzle.split("\n")
    lineno = 0
    for line in lines:
        lineno += 1
        m = re.match(r'^([^#]*)#', line)   # Remove comments
        if m:
            line = m.group(1)
        m = re.match(r'^\s+(.*)$', line)
        if m:
            line = m.group(1)
        m = re.match(r'^(.*)\s+$', line)
        if m:
            line = m.group(1)
        if re.match(r'^\s*$', line):     # Ignore blank lines
            continue
        
        nrow += 1
        cs = line.split()
        if ncol > 0 and len(cs) < ncol:
            raise SelectError("cols not identical in line: lineno")

        if len(cs) > ncol:
            ncol = len(cs) 
        rowcols.append(cs)

    if ncol != nrow:
        raise SelectError(f"number of cols{ncol} != number of rows{nrow}")
    g.nRow = nrow
    g.nCol = ncol
    g.nSubCol = int(sqrt(g.nCol))
    g.nSubRow = int(sqrt(g.nRow))
    
    puzzle = SudokuPuzzle(rows=nrow, cols=ncol, grows=g.nSubRow, gcols=g.nSubCol,
                          desc="Internal Puzzle")
    for ri in range(nrow):
        row = ri+1
        for ci in range(ncol):
            col = ci+1
            val = rowcols[ri][ci]
            if val == '-':
                continue         # Empty cell
            
            puzzle.add_cell(row=row, col=col, val=int(val))
    set_puzzle(puzzle)



# Clear to an empty board
def clear_board():
    g.o_data.clear()
    g.o_board.showData(g.o_data)



# Close move display window
def display_close():
    ###global Display_mw
    '''
    if Display_mw is not None:
        Display_mw.destroy()
    ''' 
    g.res_group.destroy_all()
    if g.o_board is not None:
        g.o_board.destroy()
        g.o_board = None
    SudokuPly.setDisplay(None)

Display_prev_time = None
def display_rtn(o_data, display_time):
    """ Progress display routing
    """
    global Display_prev_time
    now = time.time()
    if g.Display_time is not None and g.Display_mw is None:
        display_setup()
    if Display_prev_time is None:
        Display_prev_time = now
    time_end = Display_prev_time + display_time
    while True:
        now = time.time()
        if now >= time_end:
            break
        update()
        g.mw.after(int(1000*g.Display_time))
    
    SlTrace.lg(f"display_rtn time:{now}")
    Display_prev_time = time.time()   # Record for subsequent check
    g.Display_board.showData(o_data)



# Setup move display
def display_setup():
    ###global g.Display_mw, g.Display_board
    
    if g.Display_time is None:
        SudokuPly.setDisplay(None)   # Disable display
        return

    g.Display_prev_time = time.time()

    if g.Display_mw is not None:
        return     # Already setup

    title = "Solution Try"
    SudokuPly.setDisplay(display_rtn, g.Display_time)

    g.Display_mw = Toplevel()
    g.Display_mw.title(title)
    x = 400
    y = 600
    g.Display_mw.geometry(f"+{x}+{y}")
    
    top_fr = Frame(g.Display_mw)
    top_fr.pack(side = 'top')
    c1 = Button(top_fr, 
        text = "Close",               # Guess one
        command = display_close,
            )
    c1.pack(side = 'left')
    g.Display_board = SudokuBoard(mw=g.Display_mw,
                            data = g.o_data,
                            bdWidth=g.sSize*.8,
                            bdHeight=g.sSize*.8,
                            initialData=g.Initial_data,
                            )  

def file_open():
    """ Choose puzzle file
    """
    start_dir = r"./puzzle"
    filename =  filedialog.askopenfile(
        initialdir = start_dir,
        title = "Select puzzle file",
        filetypes = (("supz files","*.supz"),("all files","*.*")))
    spl = SudokuPuzzleLoad.set_input(pfile=filename)
    puzzle = spl.procCmdString()
    set_puzzle(puzzle)


# Create puzzle with number of cells filled in
# Set initial_data to this

def make_puzzle(nfilled=None):
    """ Create puzzle with number of cells filled in
    Set reset_data to this
    :nfilled: Number of cells filled in, None = random
    """
    ###global o_data, o_board
    
    display_close()
    if (g.o_data is None):
        g.o_data  = SudokuData(cols=g.nCol,
            rows=g.nRow,
            gcols=g.nSubCol,
            grows=g.nSubRow,
            )

    g.o_data.clear()          # Clear data

    if g.o_board is None:
        g.o_board = SudokuBoard(mw=g.mw,
            frame=new_main_bd_frame(),
             data=g.o_data,
             bdWidth=g.bSize,
             bdHeight=g.bSize)
 
  


    ncell = g.nRow*g.nCol
    if (nfilled is None):
        nfilled = int(ncell/3)
    if nfilled & 1 != 0 and ncell & 1 != 0:
        nfilled -= 1     # No possible symitry
                                                # with odd # and even row/col

    o_list = SudokuData(base=g.o_data)
    a_start_list = o_list.startCells(
            nFilled=nfilled,  
            symRules=g.makePuzzleSym)
    if (a_start_list is None):
        SlTrace.lg(f"no such pattern for nRow=:{g.nRow}, nCol=:{g.nCol}"
            + f" nFilled={nfilled} symRules={g.makePuzzleSym}")
        sys.exit("quitting")
    # Display start list
    sl = SudokuData(rows=g.nRow, grows=g.nSubRow, cols=g.nCol, gcols=g.nSubCol)        # for diagnostic display
    SlTrace.lg(f"start list: ")
    n = 0
    for sc in a_start_list:
        val = n
        if (n <= ord('Z')-ord('A')):
            val = chr(ord('A')+n)
        elif (n < 2*(ord('Z')-ord('A'))):
            val_ord = ord('a')+n-((ord('Z')-ord('A')-1))
            val = chr(val_ord)

        sl.setCellVal(sc.row, sc.col,
                val)
        SlTrace.lg(f" (r:{sc.row}, c:{sc.col})")
        n += 1

    sl.display()
    
    if (len(a_start_list) != nfilled):
        SlTrace.lg(f"Actual list = {len(a_start_list)}"
            + f" Requested list = {nfilled}")

                            # Set starting arrangement
    o_sol = SudokuPly(base=g.o_data)
    sols = o_sol.makePuzzle(
                    startList=a_start_list)
    if sols is not None and len(sols) == 1 and defined(sols[0]):
        sol = sols[0]
        g.o_data = sol.getData(subset=a_start_list)
        g.o_board.showData(g.o_data)
        g.Initial_data = SudokuData(base=g.o_data)

    return sols

main_bd_fr = None           # Set if present
def new_main_bd_frame():
    """ Create a new main board frame
    Deleat old frame if present
    """
    global main_bd_fr
    
    if main_bd_fr is not None:
        main_bd_fr.destroy()
    main_bd_fr = Frame(g.top_fr)
    main_bd_fr.pack(side = 'bottom')
    return main_bd_fr

    
# Adjust puzzle to a unique puzzle
# Generally by adding starting filled cells
def adj_puzzle_uniq(sols, nfilled):   # Returns: puzzle solution Ply
    sol = sols[0]
    val_max = g.nRow
    if g.nCol > val_max:
        val_max = nCol 
    SlTrace.lg(f"adj_puzzle_uniq\n")
    sol_data = sol.getData()
    for i in range(nfilled):
        nr = int(rand(nRow)+1)
        nc = int(rand(nCol)+1)
        g.o_data.curCell(row=nr, col=nc)
        r_c = None
        ntry = 0
                                # Space values randomly
        min_choice = 2     # Attempting to leave multiple choices
        tmc = val_max     # Only look so much
        legalvals = []        # choices for candidate cell
        while True:
            for i1 in range(rand(val_max)+1):
                r_c = o_data.getNextEmpty()
    
            if r_c is not None:
                break    # No more empty
      
            legalvals = g.o_data.getLegalVals(r_c['row'],
                        r_c['col'])
            tmc -= 1
            if tmc <= 0 or len(legalvals) >= min_choice:
                break
        
        if (r_c is None):
            SlTrace.lg(f"Can't find room for puzzle")
            break
        
        nr = r_c['row']
        nc = r_c['col']
        g.o_data.setCellVal(nr, nc, sol_data.getCellVal(nr, nc))
    
    
    sol = uniq_sol(g.o_data)     # Make unique
    return sol



# Reset to initial board
def reset_board():
    g.o_data = SudokuData(base=g.Initial_data)
    g.o_board.showData(g.o_data)



# Setup move display
def set_move_display(display_time):
    ###global Display_time
    
    g.Display_time = display_time




# OK to selection
def set_selected_ok():
    selecteds = g.sbox.curselection()
    si = selecteds[0]
    if si is None:
        set_selected_delete()
        return
    
    
    selected_val = g.sbox_legal_vals[si]
    g.o_data.setCellVal(g.sbox_row, g.sbox_col, selected_val)
    g.o_board.showData()
    set_selected_delete()



# CANCEL to selection
def set_selected_cancel():
    set_selected_delete()



# Remove set_selected
def set_selected_delete():
    sbox_fr.destroy() 
    if exists(sbox_fr):
        sbox = None



# Solve Puzzle 
def solve_puzzle_set():
    g.res_group.destroy_all()           # Clearout result displays
    solutions = []                       # Puzzle solution(s)
    if g.o_board is not None:
        g.o_data = g.o_board.getData()
    
    display_setup()
    Initial_data = g.o_data              # Record initial data
    solutions = solve_puzzle(data=g.o_data)
    if len(solutions) == 0:
        SlTrace.lg("No solution to puzzle")
    else:
        nsol = len(solutions)
        SlTrace.lg(f"Puzzle solved - {nsol} solution"
          + f"{'' if nsol == 1 else 's'}")
        nth = 0
        for r_solution in solutions:
            nth += 1
            solve_puzzle_set_display(r_solution,
                         f"Solution {nth} of {nsol}",
                        nth,
                        nsol)


#
def solve_puzzle_set_display(r_solution, title=None, nth=None, nsol=None):
    """ Add solution display
    :r_position of solution:
    :nth: ord positionof solution
    :nsol: Number of solutions
    """

    if title is not None:
        title = "Solution" 
    if nsol is not None:
        nsol = 1 
    
    mw = Toplevel()
    mw.title(title)
    x = 400
    y = 200
    x += 100*nth
    y += 100*nth
    mw.geometry(f"+{x}+{y}")
    # Find first empty slot, extending if necessary
    top_fr = Frame(mw)
    top_fr.pack(side = 'top')
    c1 = Button(top_fr, 
        text = "Close",               # Guess one
        command = [solve_puzzle_close, nth],
            )
    c1.pack(side = 'left')
    if nsol > 1:
        c2 = Button(top_fr, 
                     text = "Close All",               # Close all
                     command = solve_puzzle_close_all,
                    )
        c2.pack(side = 'left')
        
        
    board = SudokuBoard(mw=mw,
                data=r_solution.getData(),
                bdWidth=g.sSize,
                bdHeight=g.sSize,
                initialData=g.Initial_data,
               )
    g.res_group.add(ResourceEntry(mw), number=nth)
    board.showData()



# Close solution window
def solve_puzzle_close(si):
    mw = g.mws[si]
    if mw is not None:
        if exists(mw):
            mw.destroy() 
        g.mws[si] = None


# Close all solution windows
def solve_puzzle_close_all():
    g.res_group.destroy_all()


def solve_puzzle(data=None):      # Returns: ref to solution, else None
    r_data = data
    if r_data is None:
        raise SelectError("solve_uzzle: data missing") 
    
    solve_puzzle_close_all()
    s_ply = SudokuPly(base=r_data)
    return s_ply.solveChoice(first=g.nFirst)



#
def uniq_sol(r_data):         # 
    """ Return a puzzle with a unique solution
    :returns: SudokuPly with one solution, else None
    """
    ###  return r_sols[0]    #### STUB
    s_ply = SudokuPly(base=g.o_data)
    sols = s_ply.solveChoice(first=g.nRow)
    while (len(sols) > 1):
        squares = []
        for ri in range(g.nRow):
            row = ri + 1
            for ci in range(g.nCol):
                col = ci + 1
                if not r_data.isEmptyCell(row, col):
                    continue 
        
        valh = {}
        for r_sol in sols:
            val = r_sol.getCellVal(row, col)
            if r_data.isEmpty(row, col):
                SlTrace.lg(f"Empty sol row={row}, col={col}")
                continue
            valh[val] = 1
        vals = valh.keys()
        nval = len(vals)     # Number of different values
        if nval > 1:
            squares.append(CellDesc(nval=nval, row=row, col=col, vals=vals))
        
        squares.sort(key=lambda cell: cell.nval)
        r_nc = squares[0]          # With most values
        r_data.setCellVal(r_nc['row'], r_nc-['col'], r_nc['vals'][0])
        s_ply = SudokuPly(base=g.o_data)
        sols = s_ply.solveChoice(first=nRow)

    return sols[0]   # stub - just return first if any

