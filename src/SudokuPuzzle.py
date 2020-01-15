#SudokuPuzzle.py
# Adapted from SudokuData.py
#################
## sudokuPuzzle ##
#################

from select_error import SelectError
from SudokuData import SudokuData

class SudokuPuzzle(SudokuData):
    

    def __init__(self, desc=None, file_name=None, **kwargs):
        """
        :description:  Description of puzzle
        :file_name: file name, if known
        """
        self.file_name=file_name
        if desc is None:
            "Basic Sudoku Puzzle"
        super(SudokuPuzzle, self).__init__(**kwargs)

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
    
    def copy(self):
        """ Copy puzzle to insulate changes in data
        :Returns: copy of data with new objects for cells
        """
        rows = self.nRow
        grows = self.nSubRow
        cols = self.nCol
        gcols = self.nSubCol
        cp = SudokuPuzzle(rows=rows, grows=grows,
                          cols=cols, gcols=gcols)
        for nr in range(1, rows+1):
            for nc in range(1, cols+1):
                val = self.getCellVal(row=nr, col=nc)
                if val is not None:
                    cp.add_cell(row=nr, col=nc, val=val)
        return cp
