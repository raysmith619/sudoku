#sudoku_vals.py
# Adapted from SudokuData.pm with just values
#################
## sudokuVals ##
#################


from select_trace import SlTrace
from select_error import SelectError
from SudokuData import SudokuData
         
class SudokuVals:
    
    @classmethod
    def get_data(cls, sval):
        """ Convert SudokuVals to SukokuData
        :sval: SudokuVals
        """
        sd = SudokuData(rows=sval.nRow, grows=sval.nSubRow,
                        cols=sval.nCol, gcols=sval.nSubCol)
        for nr in range(1, sval.nRow+1):
            for nc in range(1, sval.nCol+1):
                val = sval.getCellVal(row=nr, col=nc)
                if val is not None:
                    sd.setCellVal(row=nr, col=nc, val=val)
        return sd                
    
    @classmethod
    def get_vals(cls, data):
        """ Convert to SudokuVals from SukokuData or subclasses
        :data: SudokuData, SudokuPly, SudokuPuzzle
        """
        dv = SudokuVals(rows=data.nRow, grows=data.nSubRow,
                        cols=data.nCol, gcols=data.nSubCol)
        for nr in range(1, data.nRow+1):
            for nc in range(1, data.nCol+1):
                val = data.getCellVal(row=nr, col=nc)
                if val is not None:
                    dv.setCellVal(row=nr, col=nc, val=val)
        return dv                

    def __init__(self, rows=None, cols=None, grows=None, gcols=None, 
        base = None):
        """
        :rows:  number of rows down the whole board
        :cols: number of cols accross the whole board
        :grows: group numbers for conversions to 
        :gcols: group numbers
        """
        if rows is None:
            if base is None:
                raise SelectError("Neither base nor rows was specified")
            
            rows = base.nRow
            grows = base.nSubRow
        self.nRow = rows
        self.nSubRow = grows
        if cols is None:
            if base is None:
                raise SelectError("Neither base nor cols was specified")
            
            cols = base.nCol
            gcols = base.nSubCol
        self.nCol = cols
        self.nSubCol = gcols
        self.vals = [[None for ci in range(self.nCol)] for ri in range(self.nRow)]
        if base is not None:
            for ir in range(base.nRow):
                for ic in range(base.nCol):
                    self.vals[ir][ic] = base.vals[ir][ic]

    def getCellVal(self, row=None, col=None):
        """ get cell Value
        :row: row number
        :col: col number
        """
        if row < 1 or row > self.nRow:
            raise SelectError(f"bad row({row}) value should be 1-{self.nRos}")
        
        if col < 1 or col > self.nCol:
            raise SelectError(f"bad row({row}) value should be 1-{self.nRos}")
        
        return self.vals[row-1][col-1]

    def setCellVal(self, row=None, col=None, val=None):
        """ set cell Value
        :row: row number
        :col: col number
        :val: cell value default: None
        """
        if row < 1 or row > self.nRow:
            raise SelectError(f"bad row({row}) value should be 1-{self.nRos}")
        
        if col < 1 or col > self.nCol:
            raise SelectError(f"bad row({row}) value should be 1-{self.nRos}")
        
        self.vals[row-1][col-1] = val
    # Check if empty
    # any non-zero numeric is filled 
    def isEmpty(self, val=None):      # Returns: True iff empty value
        if val is None or val == "0" or val == 0:
            return True
        
        return False


    def destroy(self):
        """ Release any resources, cleanup display
        """
        pass            # Nothing for now
    
    # Simple display of data area
    # For diagnostic purposes
    def display(self, msg=None):
        display_str = ""
        if msg is None:
            msg = "Data Display"
        display_str += f"{msg}\n"
        if self.vals is None:
            raise SelectError("data gone")

        horiz_grp_divider = " " + "-" * (2*self.nCol+self.nSubCol-1) + "\n"             
        for nr in range(1, self.nRow+1):
            if nr % self.nSubRow == 1:
                display_str += horiz_grp_divider
            for nc in range(1, self.nCol+1):
                if nc == 1:
                    display_str +="|"
                val = self.getCellVal(row=nr, col=nc)
                disp = "  " if self.isEmpty(val) else f"{val} "
                display_str += disp
                if nc % self.nSubCol == 0:
                    display_str += "|"
            display_str += "\n"
        display_str += horiz_grp_divider
        SlTrace.lg(display_str)
