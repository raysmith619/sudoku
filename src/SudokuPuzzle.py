#SudokuPuzzle.py
# Adapted from SudokuData.py
#################
## sudokuPuzzle ##
#################

from select_error import SelectError
from SudokuData import SudokuData

class SudokuPuzzle(SudokuData):
    

    def __init__(self, desc=None, **kwargs):
        """
        :description:  Description of puzzle
        """
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
            file = open(file)
        puzzle_str = file.splitlines()
        puzzle = self.str2puzzle(puzzle_str)
        return puzzle
    
        