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

import sudoku_globals as gb
from SudokuData import SudokuData, CellDesc
from sudoku_vals import SudokuVals
from SudokuPuzzle import SudokuPuzzle
from SudokuBoard import SudokuBoard
from SudokuPly import SudokuPly
from sudoku_puzzle_load import SudokuPuzzleLoad
from sudoku_search_stop import SudokuSearchStop



def helpstr():
  retstr = f"""
    --cols number_of_cols Default: {gb.nCol}
    --bSize bd size in inches Default: {gb.bSize}
    --dispalyTime sec between display, 0 - wait till user ACK
    --first number_of_solutions, stop when we have this many Default: {gb.nFirst}
    --makePuzzle starting_cells, make puzzle with this many filled cells
    --gcols number_of_cells_in_group Default: {gb.nSubCol}
    --grows number_of_cells_in_group Default: {gb.nrowGroup}
    --rows number_of_rows Default: {gb.nRow}
    --sSize solution bd size inches Default: {gb.sSize}
    --traceList comma_separated_trace_options Default: {gb.traceList}
    --uPuzzle - use preformed puzzle
    --xperimental experimental version Default: {gb.xPer}
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
    if not gb.running:
        return
    
    if not SlTrace.runningJob:
        return
    
    if gb.Display_mw is not None:
        gb.Display_mw.update()                                                                                                                                                                

def pgm_exit():
    SlTrace.lg("Quitting Sudoku Playing")
    # Trace and Log files save by SlTrace onexit
    ###SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    ###SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    gb.res_group.destroy_all()
    gb.Display_mw.destroy()
    gb.Display_mw = None
    gb.running = False
    SlTrace.onexit()        # Force saving
    sys.exit(0)

def set_controls():
    cF = SelectControl()        # Ref to singleton
    if gb.vC is not None:
        gb.vC.destroy()
        gb.vC = None
    gb.vC = VariableControl(var_ctl=cF)


def set_puzzle(puzzle, file_name=None):
    """ Set/Reset main puzzle
    :puzzle: Puzzle to setup
    """
    if file_name is not None:
        puzzle.file_name = file_name    # override if desired
    if gb.main_puzzle is not None:
        gb.main_puzzle.destroy()
        gb.main_puzzle = None
    if gb.o_board is not None:
        gb.o_board.destroy()
    gb.main_puzzle = puzzle.copy()       # Insulate from changes
    gb.puzzle = puzzle
    gb.o_board = SudokuBoard(mw=gb.Display_mw,
        frame=new_main_bd_frame(),
        data=puzzle,
        bdWidth=gb.bSize,
        bdHeight=gb.bSize,
        puzzle = puzzle)
 
    gb.o_board.showData(force=True)
    cF = SelectControl()
    cF.set_val("nRow", gb.main_puzzle.nRow)
    cF.set_val("nSubRow", gb.main_puzzle.nSubRow)
    cF.set_val("nCol", gb.main_puzzle.nCol)
    cF.set_val("nSubCol", gb.main_puzzle.nSubCol)
    cF.update_settings()#
    
def use_puzzle(puzzle=None):
    """ Use Precreated puzzle
    Set reset_data to this
                # Pattern
                    Default: PZ1
                    n x n lines
                     - or numeric contents
    """
    ###global gb.o_data, gb.nCol, gb.nSubCol, gb.nRow, gb.nrowGroup, gb.o_board, gb.Initial_data, gb.nRow, gb.nCol
    
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
    gb.nRow = nrow
    gb.nCol = ncol
    gb.nSubCol = int(sqrt(gb.nCol))
    gb.nSubRow = int(sqrt(gb.nRow))
    
    puzzle = SudokuPuzzle(rows=nrow, cols=ncol, grows=gb.nSubRow, gcols=gb.nSubCol,
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
    puzzle = SudokuPuzzle(rows=gb.nRow, cols=gb.nCol, grows=gb.nSubRow, gcols=gb.nSubCol,
                          desc="Internal Puzzle")
    set_puzzle(puzzle)
    


# Close move display window
def search_stop():
    ###global Display_mw
    '''
    if Display_mw is not None:
        Display_mw.destroy()
    '''
    SlTrace.lg("search_stop")
    SudokuPly.stop_search()
    gb.res_group.destroy_all()


display_prev_time = None
display_no = 0
def display_rtn(data):
    """ Progress display routing
    """
    global display_prev_time
    global display_no
    
    if not gb.running:
        return
    
    display_no += 1
    ###gb.main_puzzle.display("display_rtn: main_puzzle")
    display_time = gb.Display_time
    if display_time is None:
        return
    
    now = time.time()
    new_board = False
    searching_board = gb.res_group.get_obj("searching_board")
    if searching_board is None:
        solution_search_display_setup()
        new_board = True
    searching_board = gb.res_group.get_obj("searching_board")
        
    if display_prev_time is None:
        display_prev_time = now
    gb.Display_mw.after(int(1000*display_time))
    if now - display_prev_time > gb.update_time:
        puzzle_name = "INTERNAL"
        if gb.puzzle.file_name is not None:
            puzzle_name = os.path.basename(gb.puzzle.file_name)
        gb.main_puzzle.trace_check(prefix=puzzle_name)
        ###SlTrace.lg(f"{puzzle_name} move:{nmove} empty: {nempty} backup: {nbackup} time:{dur:.3f}")
        display_prev_time = now
    if searching_board is not None:
        searching_board.showData(data, force=new_board)
    if SlTrace.trace("display_board"):
        searching_board.display(f"display:{display_no}")


# Setup move display
def solution_search_display_setup():

    title = "Solution Searching"
    SudokuPly.setDisplay(display_rtn, gb.Display_time)

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
    if gb.res_group.get("searching_board") is not None:
        gb.res_group.destroy("searching_board")
    data = SudokuData.vals2data(gb.main_puzzle)  
    searching_board = SudokuBoard(mw=searching_mw,
                            data = data,
                            bdWidth=gb.sSize*.8,
                            bdHeight=gb.sSize*.8,
                            initialData=gb.Initial_data,
                            puzzle=gb.main_puzzle
                            )
    searching_board.showData(force=True)
    gb.res_group.add(ResourceEntry(searching_board), name="searching_board")
    gb.main_puzzle.set_start_time()
    
def file_proc(filename, run_after_load=None):
    """ Process (solve) one puzzle file
    :filename: full file name may be a puzzle or list of puzzle files
    :run_after_load:    True -> solve after loading, False just display
                        Default: gb.run_after_load
    """
    if not gb.running:
        return

    if filename.endswith(".supzl"):
        filelist_proc(filename)
        return
    
    if run_after_load is None:
        run_after_load = gb.run_after_load
    spl = SudokuPuzzleLoad.set_input(pfile=filename)
    if spl is None:
        return
    
    SlTrace.lg(f"Puzzle file name:{filename}")
    puzzle = spl.procCmdString()
    set_puzzle(puzzle, file_name=filename)
    puzzle.display("Puzzle Start")
    if run_after_load:
        solve_main_puzzle()

file_list_files = {}        # Used file list files
def filelist_proc(filename):
    """ Process file containing list of puzzle files
    :filename: filename of file containing list of puzzle files
            Default directory for files in list is dir(filename)
    """
    with open(filename) as f:
        file_list_files[filename] = 1   # Record as being used
        lines = f.readlines()
        filedir = os.path.dirname(filename)
    for i in range(len(lines)):
        line = lines[i]
        ml = re.match(r'^(\.*)#.*$', line)
        if ml:
            line = ml[1]    # Before comment
        line = line.strip()
        if re.match(r'^\s*$', line):
            continue                # Skip blank lines
        name = line
        if not os.path.isabs(name):
            name = os.path.join(filedir, name)
        if name in file_list_files:
            SlTrace.lg(f"file: {file} already used - avoiding recursive use ")
            continue
        file_proc(filename=name, run_after_load=True)
    
    
def file_open():
    """ Choose puzzle file
    """
    start_dir = r"./puzzle"
    filename =  filedialog.askopenfilename(
        initialdir = start_dir,
        title = "Select puzzle file",
        filetypes = (("puzzle files","*.supz"),("puzzle lists","*.supzl"),("all files","*.*")))
    file_proc(filename)


# Create puzzle with number of cells filled in
# Set initial_data to this

def make_puzzle(nfilled=None):
    """ Create puzzle with number of cells filled in
    Set reset_data to this
    :nfilled: Number of cells filled in, None = random
    """
    ###global o_data, o_board
    
    display_close()
    if (gb.o_data is None):
        gb.o_data  = SudokuData(cols=gb.nCol,
            rows=gb.nRow,
            gcols=gb.nSubCol,
            grows=gb.nSubRow,
            )

    gb.o_data.clear()          # Clear data

    if gb.o_board is None:
        gb.o_board = SudokuBoard(mw=gb.mw,
            frame=new_main_bd_frame(),
             data=gb.o_data,
             bdWidth=gb.bSize,
             bdHeight=gb.bSize)
 
  


    ncell = gb.nRow*gb.nCol
    if (nfilled is None):
        nfilled = int(ncell/3)
    if nfilled & 1 != 0 and ncell & 1 != 0:
        nfilled -= 1     # No possible symitry
                                                # with odd # and even row/col

    o_list = SudokuData(base=gb.o_data)
    a_start_list = o_list.startCells(
            nFilled=nfilled,  
            symRules=gb.makePuzzleSym)
    if (a_start_list is None):
        SlTrace.lg(f"no such pattern for nRow=:{gb.nRow}, nCol=:{gb.nCol}"
            + f" nFilled={nfilled} symRules={gb.makePuzzleSym}")
        sys.exit("quitting")
    # Display start list
    sl = SudokuData(rows=gb.nRow, grows=gb.nSubRow, cols=gb.nCol, gcols=gb.nSubCol)        # for diagnostic display
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
    o_sol = SudokuPly(base=gb.o_data)
    sols = o_sol.makePuzzle(
                    startList=a_start_list)
    if sols is not None and len(sols) == 1 and sols[0] is not None:
        sol = sols[0]
        gb.o_data = sol.getData(subset=a_start_list)
        gb.o_board.showData(gb.o_data)
        gb.Initial_data = SudokuData(base=gb.o_data)

    return sols

main_bd_fr = None           # Set if present
def new_main_bd_frame():
    """ Create a new main board frame
    Deleat old frame if present
    """
    global main_bd_fr
    
    if main_bd_fr is not None:
        main_bd_fr.destroy()
    main_bd_fr = Frame(gb.top_fr)
    main_bd_fr.pack(side = 'bottom')
    return main_bd_fr

    
# Adjust puzzle to a unique puzzle
# Generally by adding starting filled cells
def adj_puzzle_uniq(sols, nfilled):   # Returns: puzzle solution Ply
    sol = sols[0]
    val_max = gb.nRow
    if gb.nCol > val_max:
        val_max = nCol 
    SlTrace.lg(f"adj_puzzle_uniq\n")
    sol_data = sol.getData()
    for i in range(nfilled):
        nr = int(rand(nRow)+1)
        nc = int(rand(nCol)+1)
        gb.o_data.curCell(row=nr, col=nc)
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
      
            legalvals = gb.o_data.getLegalVals(r_c['row'],
                        r_c['col'])
            tmc -= 1
            if tmc <= 0 or len(legalvals) >= min_choice:
                break
        
        if (r_c is None):
            SlTrace.lg(f"Can't find room for puzzle")
            break
        
        nr = r_c['row']
        nc = r_c['col']
        gb.o_data.setCellVal(nr, nc, sol_data.getCellVal(nr, nc))
    
    
    sol = uniq_sol(gb.o_data)     # Make unique
    return sol



# Reset to initial board
def reset_board():
    gb.o_data = SudokuData(base=gb.Initial_data)
    gb.o_board.showData(gb.o_data)



# Setup move display
def set_move_display(display_time):
    ###global Display_time
    
    gb.Display_time = display_time




# OK to selection
def set_selected_ok():
    selecteds = gb.sbox.curselection()
    si = selecteds[0]
    if si is None:
        set_selected_delete()
        return
    
    
    selected_val = gb.sbox_legal_vals[si]
    gb.o_data.setCellVal(gb.sbox_row, gb.sbox_col, selected_val)
    gb.o_board.showData()
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
    gb.res_group.destroy_all()
    SudokuPly.setDisplay(None)

def update_report(ctl=None):
    """ Report control variable (cF) update
    ctl: control reference for convenience
    """
    gb.update_control_variables()
    
    

# Solve Puzzle 
def solve_main_puzzle():
    gb.solve_start = time.time()         # Puzzle start time
    gb.main_puzzle.display("solve_main_puzzle before destroy_all: main_puzzle")
    gb.res_group.destroy_all()           # Clearout result displays
    solutions = []                       # Puzzle solution(s)
    gb.main_puzzle.display("solve_main_puzzle: main_puzzle")
    solution_search_display_setup()
    Initial_data = gb.main_puzzle              # Record initial data
    
    SudokuPly.clear_search_stop()
    try:
        data = SudokuData.vals2data(gb.main_puzzle)
        solutions = solve_puzzle(data=data, puzzle=gb.main_puzzle)
        puzzle_file_name = gb.puzzle.file_name
        dur = time.time() - gb.solve_start
        nmoves = gb.main_puzzle.nmove
        sol_time = f"in {dur:.2f} sec"
        if puzzle_file_name is None:
            puzzle_name = ""
        else:
            puzzle_name = os.path.basename(puzzle_file_name)
        if len(solutions) == 0:
            SlTrace.lg(f"EndPuzzle {puzzle_name} No solution to puzzle {nmoves} moves  {sol_time}")
        else:
            nsol = len(solutions)
            SlTrace.lg(f"EndPuzzle {puzzle_name} solved - {nsol} solution{'' if nsol == 1 else 's'}"
                        + f" {nmoves} moves {sol_time}"
                        )
            searching_board = gb.res_group.get_obj("searching_board")
            if searching_board is not None:
                searching_board.trace_check(prefix=puzzle_name)
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
        gb.res_group.destroy_all()
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
                bdWidth=gb.sSize,
                bdHeight=gb.sSize,
                initialData=gb.Initial_data,
               )
    gb.res_group.add(ResourceEntry(mw), number=nth)
    board.showData(force=True)



# Close solution window
def solve_puzzle_close(si):
    mw = gb.mws[si]
    if mw is not None:
        if exists(mw):
            mw.destroy() 
        gb.mws[si] = None


# Close all solution windows
def solve_puzzle_close_all():
    gb.res_group.destroy_all()


def solve_puzzle(data=None, puzzle=None):      # Returns: ref to solution, else None
    r_data = data
    if r_data is None:
        raise SelectError("solve_uzzle: data missing") 
    
    solve_puzzle_close_all()
    s_ply = SudokuPly(base=r_data, puzzle=puzzle)
    return s_ply.solveChoice(first=gb.nFirst)



#
def uniq_sol(r_data):         # 
    """ Return a puzzle with a unique solution
    :returns: SudokuPly with one solution, else None
    """
    ###  return r_sols[0]    #### STUB
    s_ply = SudokuPly(base=gb.o_data)
    sols = s_ply.solveChoice(first=gb.nRow)
    while (len(sols) > 1):
        squares = []
        for ri in range(gb.nRow):
            row = ri + 1
            for ci in range(gb.nCol):
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
        s_ply = SudokuPly(base=gb.o_data)
        sols = s_ply.solveChoice(first=nRow)

    return sols[0]   # stub - just return first if any

