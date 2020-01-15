#sudoku_vals.py
# Adapted from SudokuData.pm with just values
#################
## sudokuVals ##
#################


from select_trace import SlTrace
from select_error import SelectError

EMPTY = 0               # Empty cell def         


class CellDesc:
    """ Cell description
    """
    def __init__(self, row=None, col=None,
                  val=None, vals=[], valId=None):
        """ Cell description row,col, optionally value
        """
        self.row = row
        self.col = col
        self.val = val
        self.vals = vals
        self.valId = valId
        x1 = x2 = y1 = y2 = None
    
    def copy(self):
        """ Copy info
        :Returns: deep copy
        """
        cp = CellDesc(row=self.row, col=self.col, val=self.val,
                      vals=self.vals[:], valId=self.valId)
        return cp

class ValueChoice:
    """ Attributes of a selection choice
    """
    def __init__(self, vals=None, row=None, col=None, nval=None):
        self.vals = vals
        self.row = row
        self.col = col
        self.nval = nval
    
    def __repr__(self):
        repr_str = "ValueChoice"
        repr_str += f" row={self.row} col={self.col} nval={self.nval}"
        if self.vals is not None and len(self.vals) > 0:
            vals_strs = list(map(str, self.vals))
            repr_str += f" vals=[{'<'.join(vals_strs)}]"
        return repr_str



class SudokuVals:
    EMPTY = 0

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
        self.vals = [[EMPTY for ci in range(self.nCol)] for ri in range(self.nRow)]
        if base is not None:
            for ir in range(base.nRow):
                for ic in range(base.nCol):
                    self.vals[ir][ic] = base.vals[ir][ic]

    # Clear data to empty
    def clear(self):
        for ir in range(self.nRow):
            for ic in range(self.nCol):
                self.clearCell(row=ir+1, col=ic+1)
    
    # Clear sell
    def clearCell(self, row=None, col=None):
        self.setCellVal(self, row=row, col=col, val=EMPTY)
        
    def copy(self):        # Returns: deep copy
        copy = SudokuVals(base=self)
        return copy
    
    # Get cell info
    def getCell(self, row, col):       # Returns: data cell
        val = self.getCellVal(row=row, col=col)
        cell = CellDesc(row=row, col=col, val=val)
        return cell

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

    def setCell(self, row=None, col=None, val=None):
        """ set cell Value
        :row: row number
        :col: col number
        :val: cell value default: None
        """
        self.setCellVal(row=row, col=col, val=val)
        return CellDesc(row=row, col=col, val=val)
    
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
        if SlTrace.trace("setCell"):
            SlTrace.lg(f"setCellVal row={row} col={col} val={val}")
        self.vals[row-1][col-1] = val

    # Check if empty
    # any non-zero numeric is filled 
    def isEmpty(self, val=None):      # Returns: True iff empty value
        if val is None or val == "0" or val == 0:
            return True
        
        return False
    
    # Is cell empty
    def isEmptyCell(self, row, col):       # Returns: True iff empty cell
        val = self.getCellVal(row, col)
        return self.isEmpty(val)

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
    
    # Assemble list of next move choices
    # sorted in ascending number of values per cell
    def getChoices(self):       # Returns: ref to sorted array of choices
        cells = []          # Array of open cell cells
                            # to be ordered in increasing
                            # number of values
        for ri in range(self.nRow):
            row = ri + 1
            for ci in range(self.nCol):
                col = ci + 1
                if self.isEmptyCell(row=row, col=col):
                    cells.append(CellDesc(row=row, col=col))
    
        return self.orderChoices(cells)
    
    # Assemble list of next move choices
    # sorted in ascending number of values per cell
    @staticmethod
    def _choices_cmp_val(elm):
        return elm.nval
    
    def orderChoices(self, cells):
        """
        :cells:  List of cells
        :returns: ref to sorted array of choices 
                           # to be ordered in increasing
                            # number of values
        """                            
        choices = []        # Populated with 
        for cell in cells:
            col = cell.col
            row = cell.row
            if not self.isEmptyCell(row, col):
                continue
                
            vals = self.getLegalVals(row, col)
            nval = len(vals)
            choice = ValueChoice(vals=vals, row=row, col=col, nval=nval)
            choices.append(choice)
        choices_srt = sorted(choices, key=lambda x: x.nval)
        return choices_srt

    
    # Get data values in given column
    def getColVals(self, col=None, include_nones=None):
        """ Get values in given row
        :row: column number
        :include_nones: True - include Nones in list 
        :Returns: values in row 
        """
        if col is None or col < 1 or col > self.nCol:
            raise SelectError(f"bad col number {col}")
        
        vals = []
        for ri in range(self.nRow):
            row = ri + 1
            val = self.getCellVal(row=row, col=col)
            if include_nones or not self.isEmpty(val):
                vals.append(val)
        return vals
    
    
    def getLegalVals(self, row=None, col=None):         # Returns: array of legal values
        """ Get all values for given cell given other cells in data
        Returns array, possibly empty of legal cell values
        returned values are sorted in ascending order
        cks for defined row,col and out of bounds
        :row: row to consider
        :col: col to consider
        :returns: sorted candidate values
        """
        if (row is None or row < 1 or row > self.nRow
                or col is None or col < 1
                or col > self.nCol):          # Safety check
            return [] 
        
        usedH = {}                      # Add to list as found
                                        # Allow EMPTY
        row_vals = self.getRowVals(row)
        for row_val in row_vals:
            usedH[row_val] = 1

        col_vals = self.getColVals(col)
        for col_val in col_vals:
            usedH[col_val] = 1

        sq3_vals = self.getSq3Vals(row, col)
        for sq3_val in sq3_vals:
            usedH[sq3_val] = 1

        
        legal_vals = []
        for n in range(1, self.nRow+1):
            if n not in usedH:
                legal_vals.append(n) 
        
        if SlTrace.trace("any"):
            lvstrs = list(map(str, sorted(legal_vals)))
            SlTrace.lg(f"getLegals(row={row}, col={col} = "
                        + ", ".join(lvstrs))
        
        return sorted(legal_vals)

    def getNonEmptyCells(self):
        """ Return array of none empty cells
        """
        nonemptys = []
        for ri in range(self.nRow):
            for ci in range(self.nCol):
                val = self.vals[ri][ci]
                if not self.isEmpty(val):
                    row = ri+1
                    col = ci+1
                    nonemptys.append(CellDesc(row=row, col=col, val=val))
        return nonemptys

    def getRowVals(self, row=None, include_nones=None):       # Returns: row values
        """ Get values in given row
        :row: column number
        :include_nones: True - include Nones in list 
        :Returns: values in row 
        """
        if row is None or row < 1 or row > self.nRow:
            raise SelectError(f"bad row number :{row}") 
        
        vals = []
        for ci in range(self.nCol):
            col = ci + 1
            val = self.getCellVal(row=row, col=col)
            if include_nones or not self.isEmpty(val):
                vals.append(val)
        return vals
    
    # 
    def getSq3Vals(self, row=None, col=None):
        """ Get valuse in sub-by-sub square
        :row:  current row
        :col: current col
        :Returns: list of values in current sub square
        """
        if row is None or row < 1 or row > self.nRow:
            raise SelectError(f"bad row {row}")
         
        if col is None or col < 1 or col > self.nCol:
            raise SelectError(f"bad col {col}")
        
        sq3_vals = []
        first_row = 1 + self.nSubRow*int((row-1)/self.nSubRow)
        first_col = 1 + self.nSubCol*int((col-1)/self.nSubCol)
        for ir in range(self.nSubRow):
            for ic in range(self.nSubCol):
                r = first_row + ir
                c = first_col + ic
                val = self.getCellVal(r, c)
                if not self.isEmpty(val):  # Assumes no duplicates
                    sq3_vals.append(val)

        
        if SlTrace.trace("any"):
            sq3_vals_strs = list(map(str, sq3_vals))
            SlTrace.lg(f"getSq3Vals(row={row}, col={col}) = "
              + ", ".join(sq3_vals_strs)) 
        return sq3_vals
    
    def isValid(self):
        """ Check for valid arrangement
        """
        for ir in range(self.nRow):     # Check rows for duplicates
            row = ir + 1
            vals = {}
            for ic in range(self.nCol):
                col = ic + 1
                val = self.getCellVal(row=row, col=col)
                if not self.isEmpty(val):
                    if val in vals:
                        SlTrace.lg(f"doing row {row} at col={col} val={val} vals={vals} invalid")
                        SlTrace.lg(f"row:{row} vals: {self.getRowVals(row)} col:{col} vals: {self.getColVals(col)}")
                        return False
                    vals[val] = val
            
        for ic in range(self.nCol):     # Check cols for duplicates
            col = ic + 1
            vals = {}
            for ir in range(self.nRow):
                row = ir + 1
                val = self.getCellVal(row=row, col=col)
                if not self.isEmpty(val):
                    if val in vals:
                        SlTrace.lg(f"at row={row} doing col={col} val={val}  vals={vals} invalid")
                        SlTrace.lg(f"row:{row} vals: {self.getRowVals(row)} col:{col} vals: {self.getColVals(col)}")
                        return False
                    vals[val] = val
        return True    
