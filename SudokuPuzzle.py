#SudokuPuzzle.py
# Adapted from SudokuData.py
#################
## sudokuPuzzle ##
#################
import time
from select_trace import SlTrace
from select_error import SelectError
from SudokuData import SudokuData

class SudokuPuzzle(SudokuData):
    

    def __init__(self, desc=None, file_name=None,
                    nmove=0,
                    nbackup=0,
                    **kwargs):
        """
        :description:  Description of puzzle
        :file_name: file name, if known
        :nmove: cumulative number of moves (new square values)
        :nbackup: cumulative number of backups (square value retries)
        :kwargs: parameters passed to SudokuData base class
        """
        if desc is None:
            desc = "Basic Sudoku Puzzle"
        self.nmove = nmove
        self.nbackup = nbackup
        self.file_name=file_name
        self.set_start_time()

        self.solve_start = time.time()
        self.dur = 0
        self.ply = None
        self.prev_ply = None
        self.depth = 0
        self.max_depth = 0              # Maximum ply depth reached so far
        self.nempty = 0
        self.min_nempty = None
        self.max_nempty = None
        super().__init__(**kwargs)

    def set_start_time(self):
        """ set/reset solve start time
        """
        self.solve_start = time.time()

    def add_cell(self, row=None, col=None, val=None):
        """ Add data square to puzzle 
        :row: row number
        :col: column number
        :val: square number
        """
        if row is None or col is None or val is None:
            raise SelectError(f" row, col and val must be specified row={row}, col={col}, val={val}")
        
        self.setCell(row=row, col=col, val=val)
    
    def file2puzzle(self, file=None):
        """ convert file name/object to puzzle
        :file: name if string, else open file stream
        :returns: puzzle, None if failure
        """
        if isinstance(file, str):
            self.file_name = file
            file = open(file)
        puzzle_str = file.splitlines()
        puzzle = self.str2puzzle(puzzle_str)
        return puzzle

    def track_move(self, ply=None):
        """ Track solution moves
            Check for backup here, comparing with ply.depth
            against prev_ply.depth
        :ply: SutokuPly, if known
        """
        self.dur = time.time() - self.solve_start
        self.prev_ply = self.ply
        if self.prev_ply is None:
            self.prev_ply = ply
        if ply is not None:
            self.nempty = ply.getNumEmpty()
            if self.min_nempty is None or self.nempty < self.min_nempty:
                self.min_nempty = self.nempty
            if self.max_nempty is None or self.nempty > self.max_nempty:
                self.max_nempty = self.nempty
            if ply.depth < self.depth:
                self.nbackup += 1
                SlTrace.lg(f"backup: move: {self.nmove} ply.depth:{ply.depth} < self.depth{self.depth}", "trace_move")
            self.depth = ply.depth
            if self.depth < self.prev_ply.depth:
                self.nbackup += 1
            if self.max_depth is None or self.depth > self.max_depth:
                self.max_depth = self.depth
            self.prev_ply = ply
        self.dur = time.time() - self.solve_start
        if SlTrace.trace("trace_move"):
            self.trace_check(ply=ply)
            
    def trace_check(self, ply=None, prefix=None):
        """ Do timely reporting of trace
            Check for backup here, comparing with ply.depth
            against prev_ply.depth
        :ply: SutokuPly, if known
        """
        if prefix is None:
            prefix = ""
        depth_info = ""
        sq_info = ""
        sq_info = f"empty: {self.nempty}[{self.min_nempty}-{self.max_nempty}]"
        depth_info = f" depth: {self.depth}  max depth: {self.max_depth}"
        sol_time = f"in {self.dur:.2f} sec"
        SlTrace.lg(f"{prefix} move: {self.nmove} {sq_info}  backup: {self.nbackup} {depth_info} {sol_time}")

    def new_backup(self, ply=None):
        """ Track moves - only called if explicit backup, else calculation is done implicitly
        :ply: SudokuPLy, if known
        """
        self.nbackup += 1
        self.track_move(ply=ply)
        
    def new_move(self, ply=None):
        """ Track moves
        :ply: SudokuPLy, if known
        """
        self.nmove += 1
        self.track_move(ply=ply)
            
    def copy(self):
        """ Copy puzzle to insulate changes in data
        :Returns: copy of data with new objects for cells
        """
        cp = SudokuPuzzle(rows=self.nRow, grows=self.nSubRow,
                          cols=self.nCol, gcols=self.nSubCol,
                          file_name=self.file_name,
                          nmove = self.nmove,
                          nbackup = self.nbackup)
        for ri in range(cp.nRow):
            row = ri + 1
            for ci in range(cp.nCol):
                col = ci + 1
                val = self.getCellVal(row=row, col=col)
                if val is not None:
                    cp.add_cell(row=row, col=col, val=val)
        return cp
