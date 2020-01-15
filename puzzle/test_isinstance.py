# test_isinstance.py
"""
Not seeing SudokuData
"""
from SudokuBoard import SudokuBoard
from SudokuData import SudokuData
from SudokuPly import SudokuPly

sb = SudokuBoard()
sd = SudokuData()
sp = SudokuPly()

if isinstance(sd, SudokuData):
    print(f"Found sd{sd} to be SudokuData instance")
else:
    print(f"Did not find sd{sd} to be SudokuData instance")
