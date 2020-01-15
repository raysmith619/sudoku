# sudoku_subs.py
# Top level subs for sudoku.py
# imported to workaround the lack of forward referencing subroutines
import sys
import os
from tkinter import filedialog
from tkinter import *
import time
import argparse
from math import *
from select_trace import SlTrace
from select_error import SelectError
from resource_group import ResourceEntry
from select_control import SelectControl
from variable_control import VariableControl

import sudoku_globals as g
from SudokuData import SudokuData, CellDesc
from sudoku_vals import SudokuVals
from SudokuPuzzle import SudokuPuzzle
from SudokuBoard import SudokuBoard
from SudokuPly import SudokuPly
from sudoku_puzzle_load import SudokuPuzzleLoad
from sudoku_search_stop import SudokuSearchStop



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

def update():
    """ do any window updating required
    """
    if not g.running:
        return
    
    if not SlTrace.runningJob:
        return
    
    if g.Display_mw is not None:
        g.Display_mw.update()                                                                                                                                                                

def pgm_exit():
    SlTrace.lg("Quitting Sudoku Playing")
    # Trace and Log files save by SlTrace onexit
    ###SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    ###SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    g.running = False
    g.res_group.destroy_all()
    g.Display_mw.destroy()
    g.Display_mw = None
    SlTrace.onexit()        # Force saving
    sys.exit(0)

def set_controls():
    cF = SelectControl()        # Ref to singleton
    if g.vC is not None:
        g.vC.destroy()
        g.vC = None
    g.vC = VariableControl(var_ctl=cF)


def set_puzzle(puzzle, file_name=None):
    """ Set/Reset main puzzle
    :puzzle: Puzzle to setup
    """
    if file_name is not None:
        puzzle.file_name = file_name    # override if desired
    if g.main_puzzle is not None:
        g.main_puzzle.destroy()
        g.main_puzzle = None
    if g.o_board is not None:
        g.o_board.destroy()
    g.main_puzzle = SudokuData.data2vals(puzzle)
    g.puzzle = puzzle
    g.o_board = SudokuBoard(mw=g.Display_mw,
        frame=new_main_bd_frame(),
        data=puzzle,
        bdWidth=g.bSize,
        bdHeight=g.bSize)
 
    g.o_board.showData(force=True)
    cF = SelectControl()
    cF.set_val("nRow", g.main_puzzle.nRow)
    cF.set_val("nSubRow", g.main_puzzle.nSubRow)
    cF.set_val("nCol", g.main_puzzle.nCol)
    cF.set_val("nSubCol", g.main_puzzle.nSubCol)
    cF.update_settings()#
    
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
def search_stop():
    ###global Display_mw
    '''
    if Display_mw is not None:
        Display_mw.destroy()
    '''
    SlTrace.lg("search_stop")
    SudokuPly.stop_search()
    g.res_group.destroy_all()


display_prev_time = None
display_no = 0
def display_rtn(data):
    """ Progress display routing
    """
    global display_prev_time
    global display_no
    
    if not g.running:
        return
    
    display_no += 1
    ###g.main_puzzle.display("display_rtn: main_puzzle")
    display_time = g.Display_time
    if display_time is None:
        return
    
    now = time.time()
    new_board = False
    searching_board = g.res_group.get_obj("searching_board")
    if searching_board is None:
        solution_search_display_setup()
        new_board = True
    searching_board = g.res_group.get_obj("searching_board")
        
    if display_prev_time is None:
        display_prev_time = now
    g.Display_mw.after(int(1000*display_time))
    dur = now - g.solve_start
    if now - display_prev_time > g.update_time:
        SlTrace.lg(f"display_rtn time:{dur:.3f}")
        display_prev_time = now
    if searching_board is not None:
        searching_board.showData(data, force=new_board)
    if SlTrace.trace("display_board"):
        searching_board.display(f"display:{display_no}")


# Setup move display
def solution_search_display_setup():

    title = "Solution Searching"
    SudokuPly.setDisplay(display_rtn, g.Display_time)

    searching_mw = Toplevel()
    searching_mw.protocol("WM_DELETE_WINDOW", search_stop)
    searching_mw.title(title)
    x = 400
    y = 600
    searching_mw.geometry(f"+{x}+{y}")
    
    top_fr = Frame(searching_mw)
    top_fr.pack(side = 'top')
    c1 = Button(top_fr, 
        text = "Close",               # Guess one
        command = search_stop,
            )
    c1.pack(side = 'left')
    if g.res_group.get("searching_board") is not None:
        g.res_group.destroy("searching_board")
    data = SudokuData.vals2data(g.main_puzzle)  
    searching_board = SudokuBoard(mw=searching_mw,
                            data = data,
                            bdWidth=g.sSize*.8,
                            bdHeight=g.sSize*.8,
                            initialData=g.Initial_data,
                            )
    searching_board.showData(force=True)
    g.res_group.add(ResourceEntry(searching_board), name="searching_board")
    
def file_open():
    """ Choose puzzle file
    """
    start_dir = r"./puzzle"
    filename =  filedialog.askopenfilename(
        initialdir = start_dir,
        title = "Select puzzle file",
        filetypes = (("supz files","*.supz"),("all files","*.*")))
    spl = SudokuPuzzleLoad.set_input(pfile=filename)
    SlTrace.lg(f"Puzzle file name:{filename}")
    puzzle = spl.procCmdString()
    set_puzzle(puzzle, file_name=filename)
    puzzle.display("Puzzle Start")


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

def clear_solve_main_puzzle():
    g.res_group.destroy_all()
    SudokuPly.setDisplay(None)

def update_report(ctl=None):
    """ Report control variable (cF) update
    ctl: control reference for convenience
    """
    g.update_control_variables()
    
    

# Solve Puzzle 
def solve_main_puzzle():
    g.solve_start = time.time()         # Puzzle start time
    g.main_puzzle.display("solve_main_puzzle before destroy_all: main_puzzle")
    g.res_group.destroy_all()           # Clearout result displays
    solutions = []                       # Puzzle solution(s)
    g.main_puzzle.display("solve_main_puzzle: main_puzzle")
    solution_search_display_setup()
    Initial_data = g.main_puzzle              # Record initial data
    SudokuPly.clear_search_stop()
    try:
        data = SudokuData.vals2data(g.main_puzzle)
        solutions = solve_puzzle(data=data)
        puzzle_file_name = g.puzzle.file_name
        dur = time.time() - g.solve_start
        sol_time = f"in {dur:.2f} sec"
        if puzzle_file_name is None:
            puzzle_file_name = ""
        else:
            puzzle_file_name = os.path.basename(puzzle_file_name)
        if len(solutions) == 0:
            SlTrace.lg(f"No solution to puzzle {sol_time} {puzzle_file_name}")
        else:
            nsol = len(solutions)
            SlTrace.lg(f"Puzzle solved - {nsol} solution{'' if nsol == 1 else 's'}"
                        + f" {sol_time} {puzzle_file_name}"
                        )
            nth = 0
            for r_solution in solutions:
                nth += 1
                r_solution.display(f"Solution {nth} of {nsol} {puzzle_file_name}")
                solve_main_puzzle_display(r_solution,
                             f"Solution {nth} of {nsol}",
                            nth,
                            nsol)
    except SudokuSearchStop:
        SlTrace.lg("SudokuSearchStop")
        clear_solve_main_puzzle()
        g.res_group.destroy_all()
        SudokuPly.setDisplay(None)

#
def solve_main_puzzle_display(r_solution, title=None, nth=None, nsol=None):
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
    mw.protocol("WM_DELETE_WINDOW", search_stop)
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
                data=r_solution,
                bdWidth=g.sSize,
                bdHeight=g.sSize,
                initialData=g.Initial_data,
               )
    g.res_group.add(ResourceEntry(mw), number=nth)
    board.showData(force=True)



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

