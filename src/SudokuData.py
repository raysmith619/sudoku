#SudokuData.py
# Adapted from SudokuData.pm
#################
## sudokuData ##
#################
import re
import copy
from random import randint

from select_trace import SlTrace
from select_error import SelectError

import sudoku_globals as g

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
    
        
base=None



"""
Marker difinition
"""
class CellMark:
    def __init__(self, row=None, col=None, id=None, rc=None,
                 tag=None, backColor=None, boundColor=None,
                 boundWidth=None, boundWidget=None):
        if row is None:
            row = rc.row
            col = rc.col
        self.row = row
        self.col = col
        self.id = id
        self.rc = rc,
        self.tag = tag,
        self.backColor = backColor
        self.boundWidth = boundWidth
        self.boundWidget = boundWidget
        

        
class SudokuData:
    

    def __init__(self, rows=None, grows=None, cols=None, gcols=None, 
        base = None):
        """
        :rows:  number of rows down the whole board
        :grows: number of row cells in sub square
        :cols: number of cols accross the whole board
        :gcols: number of col cells
        """
        if rows is None:
            if base is None:
                raise SelectError("Neither base nor rows was specified")
            
            rows = base.nRow
        self.nRow = rows
        if grows is None:
            if base is None:
                raise SelectError("Neither base nor grows was specified")
            
            grows = base.nSubRow
        self.nSubRow = grows
        if cols is None:
            if base is None:
                raise SelectError("Neither base nor cols was specified")
            
            cols = base.nCol
        self.nCol = cols
        if gcols is None:
            if base is None:
                raise SelectError("Neither base nor gcols was specified")
            
            gcols = base.nSubCol
        self.nSubCol = gcols

        self.curRow = self.nRow
        self.curCol = self.nCol                  # Most recently filled
        self.markH = {}                     # Marked cells
        self.cells = None                   # Array of cell data
        r_ds = None
        if base is not None:
            r_ds = base.copy_cells()
            self.curRow = base.curRow
            self.curCol = base.curCol
        self.setData(r_ds)

    
    def advanceCell(self):        # Returns CellDesc array (row,col)
        """ Advance to next data cell
        Current and only pattern is row1 col1->nCol, row2 col1->nCol, ...
        wrapping at nRow,nCol to row1,col1
        curRow, curCol are updated
        :returns: CellDesc
        """
        row = self.curRow
        col = self.curCol
        col += 1
        if col > self.nCol:
            row += 1
            col = 1
            if row > self.nRow:
                row = 1 
        self.curRow = row
        self.curCol = col
        return CellDesc(row=row, col=col)


    
    # Clear data to empty
    def clear(self):
        self.setData()
    
    
    # Clear sell
    def clearCell(self, row=None, col=None):
        if row is None or col is None:
            return
        
        self.cells[row-1][col-1] = None    

    def copy(self, ):        # Returns: deep copy
        copy = SudokuData(base=self)
        return copy

    
    # Set / Get current cell
    def curCell(self, cd=None, row=None, col=None):    # Returns: r_c ref to cell structure
        if cd is not None and (row is not None or col is not None):
            raise SelectError("curCell: cd and row,col specified - allow only cd or row,col")
        
        if cd is None and row is None and col is None:
            return CellDesc(row=self.curRow, col=self.curCol)
        
        if cd is not None:
            self.curRow = cd.row
            self.curCol = cd.col
            return cd
        
        self.curRow = row
        self.curCol = col
        return CellDesc(row=self.curRow, col=self.curCol)
    
    def destroy(self):
        """ Destroy data
        """
        pass            # Nothing for now
    
    # Simple display of data area
    # For diagnostic purposes
    def display(self, msg=None):
        display_str = ""
        if msg is None:
            msg = "Data Display"
        display_str += f"{msg}\n"
        if self.cells is None:
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
        

    def setCell(self, row=None, col=None, val=None):
        cell = self.getCell(row=row, col=col)
        if cell is None:
            raise SelectError(f"Missing Cell row={row} col={col}")
        cell.val = val    
    # 
    def setData(self, r_ds=None):
        """Set data
        clear if no  data array
        :r_ds: array
        """
        if self.cells is not None:  # Clear
            del self.cells 
        self.cells = [[CellDesc(row=ri+1, col=ci+1) for ci in range(self.nCol)] for ri in range(self.nRow)]
        if r_ds is not None:
            for ic in range(self.nRow):
                for ir in range(self.nCol):
                    clds = r_ds[ir][ic]
                    self.cells[ir][ic] = clds.copy()

    def copy_cells(self):
        """ Copy cells
        """
        new_cells = copy.deepcopy(self.cells)
        return new_cells
    
        
    # Deep copy of our data
    # copies not refs to all contained data
    def deepCopy(self):       # Returns: blessed deep copy of our data
        copy = SudokuData()
        r_c_cells = copy.cells = []
        r_cells = self.cells
        for ri in range(self.nRow):
            for ci in range(self.nCol):
                r_c_cells[ri][ci] = r_cells[ri][ci]
        copy.curRow = self.curRow
        copy.curCol =self.curCol
        r_c_markH = {}
        r_markH = self.markH
        for key in r_markH:
            r_c_markH[key] = r_markH[key]
        return copy
    
    
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
    
    
    
    # Get next empty cell
    # continues, starting with (row,col) after most recently filled
    # Returns reference to cell descriptor {row=n, col=n) if one
    #         None if no empty cell found
    #
    def getNextEmpty(self, cd=None, row=None, col=None):     # Returns: cell descriptor, else None
        if cd is not None or row is not None:
            self.curCell(cd=cd, row=row, col=col)
        cell = self.curCell()
        row = cell.row
        col = cell.col
        if (self.isEmptyCell(cell.row, cell.col)):
            self.advanceCell()
            if self.isEmptyCell(cell.row, cell.col):
                return cell 

        ncell = self.nRow*self.nCol
        ntry = 0
        if SlTrace.trace("empty"):
            SlTrace.lg("getNextEmpty()")

        while True:
            cd = self.advanceCell()
            row,col = cd.row, cd.col
            if SlTrace.trace("empty"):
                SlTrace.lg(f" getNextEmpty check row={row}, col={col}")
            ntry += 1
            val = self.getCellVal(row, col)
            if self.isEmpty(val):
                SlTrace.lg(f"getNextEmpty - got row={row}, col={col}", "empty")
                return CellDesc(row=row, col=col)      # Return empty cell descriptor

            if ntry >= ncell:
                SlTrace.lg("getNextEmpty - NONE FOUND")
                return None

    
    # Select legal/reasonable starting values for list of cells
    def pickStartValues(self, startList=None,
                    clear=True ):        # Returns: True iff possible
        a_start_list = startList
        if clear:
            self.clear()    # Start with cleared cells
        for r_c in a_start_list:
            row = r_c.row
            if row is None:
                raise SelectError("pickStartValues: bad row")
            col = r_c.col
            legals = self.getLegalVals(row, col)
            if legals == 0:
                return False

            self.setCellVal(row, col, legals[0])
        return True
    
    
    # Check if empty
    # any non-zero numeric is filled 
    def isEmpty(self, val=None):      # Returns: True iff empty value
        if val is None or val == "0" or val == 0:
            return True
        
        return False
    
    # Is cell empty
    def isEmptyCell(self, row, col):       # Returns: True iff empty cell
        cell = self.getCell(row, col)
        val = cell if cell is None else cell.val
        SlTrace.lg(f"isEmpty(row={row} col={col}) val:{val}", "empty")
        if cell is None:
            return True                 # Empty
        
        return self.isEmpty(cell.val)

    
    # Get data values in column
    def getColVals(self, col=None):       # Returns: col values
        cells = self.cells
        if col is None or col < 1 or col > self.nCol:
            raise SelectError(f"bad col {col}")
        
        col_vals = []
        for ri in range(len(cells)):
            val = self.getCellVal(row=ri+1, col=col)
            if not self.isEmpty(val):
                col_vals.append(val)
        col_vals_strs = list(map(str, col_vals))
        SlTrace.lg(f"getColVals(col={col}) = {', '.join(col_vals_strs)}", "cell_values")
        return col_vals
    
    # Get valuse in sub-by-sub square
    def getSq3Vals(self, row=None, col=None):       # Returns: col values
        self.r_data = self.cells
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

    
    
    # Get cells values in row
    def getRowVals(self, row):       # Returns: row values
        r_cells = self.cells
        if row is None or row < 1 or row > self.nRow:
            raise SelectError(f"bad row:{row}") 
        r_row = r_cells[row-1]     #DEPENDNT on cells layout
        row_vals = []
        for cell in r_row:
            val = cell.val
            if not self.isEmpty(val):
                row_vals.append(val)

        if SlTrace.trace("any"):
            row_vals_strs = list(map(str, row_vals))
            SlTrace.lg(f"getRowVals(row={row}) = "
              + ", ".join(row_vals_strs))
    
        return row_vals

    
    def setCellVal(self, row=None, col=None, val=None, quiet=False):
        """ set Sudoku cell with value - may be EMPTY
          :row:          1-nRow
          :col:          1-nCol
          :val:          EMPTY, 1-9, marking value
          :quiet:        1 -> no trace, no cell change
        """
        if (row is None or row < 1
            or row > self.nRow):
                raise SelectError(f"illegal row:{row}")
        
        if (col is None or col < 1
                or col > self.nCol):
            raise SelectError(f"illegal Col:{col} (1-{self.nCol})")
        
        
        if not quiet:               # quiet -> move invisibly also
            SlTrace.lg(f"setCellVal(row:{row}, col:{col}, val:{val})", "any")
        
        self.curRow = row
        self.curCol = col
        
        cell = self.getCell(row=row, col=col)
        cell.val = val
        return val

    
    
    #
    def startCells(self, nFilled=None, symRules=None, ):
        """ Find legal list of cells
        Sets data
        To provide atleast 2-way symitry with an
        odd lengthed board, one
        adds an "odd" cell to the board center
        cell
        :returns: list of CellDesc
        """
        if nFilled is None:
            raise SelectError("startList nFilled is missing")
        if symRules is None:
            symRules = "c"
        symRules = symRules.lower()
        sym_c = True if re.search(r'c', symRules) else False
        sym_x = True if re.search(r'x', symRules) else False
        sym_y = True if re.search(r'y', symRules) else False
        nf = 0        # Number filled
        start_cells = []    # List of start cells in order
        if nFilled % 2!= 0 and (self.nRow % 2 == 1 or self.nCol % 2 == 1):
            crow = int((self.nRow+1)/2)
            ccol = int((self.nCol+1)/2)
            self.setCellVal(crow, ccol, 1)
            start_cells.append(CellDesc(row=crow, col=ccol))
            nf += 1

        
        while nf < nFilled:
            row = randint(1,self.nRow)
            col = randint(1, self.nCol)
            r_c = self.getNextEmpty(row=row, col=col)
            if r_c is None:
                break
            row = r_c.row      # Update iff necessary
            col = r_c.col
            if sym_c:
                srow, scol = self.symCell(symRule='c',
                                          row=row,
                                          col=col)
                if self.isEmptyCell(srow, scol):
                    self.setCellVal(srow, scol, 1)
                    start_cells.append(CellDesc(row=srow, col=scol))
                    nf += 1
                                # Add original if not there
                    if (self.isEmptyCell(row, row)):
                        self.setCellVal(row, col, 1)
                        start_cells.append(CellDesc(row=row,
                                           col=col))
                        nf += 1

        return start_cells

    
    # 
    def getCell(self, row=None, col=None, quiet = False):
        """ get Sudoku cell may be EMPTY
        :row:          # 1-nRow
        :col:          # 1-nCol
        :quiet:,        # supress trace and cell movement default: False
        :returns: cell
        """
        cells = self.cells
        if row is None or row < 1 or row > self.nRow:
            raise SelectError(f"Bad row={row} col={col}")

        
        if col is None or col < 1 or col > self.nCol:
            raise SelectError(f"Bad col={col} row={row}")

        
        cell = cells[row-1][col-1]
        if cell is None:
            raise SelectError(f"Missing cell row={row} col={col}")
        
        return cell
    
    
    # Get data cell
    def getCellVal(self, row=None, col=None):
        cell = self.getCell(row=row, col=col)
        if cell is None:
            raise SelectError(f"Missing Cell row={row} col={col}")
        
        return cell.val

    
    
    # Get list of non-empty cells
    def getNonEmptyCells(self):      # Returns: array of {row=, col=}
        nonemptys = []
        r_data = self.data
        for ri in range(self.nRow):
            for ci in range(self.nCol):
                val = r_data[ri][ci]
                if not self.isEmpty(val):
                    row = ri+1
                    col = ci+1
                    nonemptys.append(CellDesc(row=row, col=col))
        return nonemptys
    
    
    # Find symetric cell
    def symCell(self, row=None, col=None, symRule=None):    # Returns: CellDesc
        if symRule is None:
            symRule = "c"
        symRule = symRule.lower()
        srow = row        # Symetric cell coord
        scol = col
        if re.search(r'x', symRule):
            scol = self.nCol-col+1
        elif re.search(r'y', symRule):
            srow = self.nRow-row+1
        elif re.search(r'c', symRule):
            srow = self.nRow-row+1
            scol = self.nCol-col+1
        return (srow, scol)

    
    
    # Remove one or all
    def unmarkCell(self, row, col):
        r_markh = self.markH
        if row is None:
            r_markh = {}     # Unmark all
        else:
            rckey = f"{row}:{col}"
            if rckey in r_markh:
                del r_markh[rckey] # Clear
        
        self.markH = r_markh    # Update stored settings

    
    
    # Mark cell
    # 
    def markCell(self, row, col):
        r_markh = self.markH
        rckey = f"{row}:{col}"
        r_markh[rckey] = 1

    
    # Check if cell is marked
    def isMarked(self, row, col):       # Returns: 1 if marked else 0
        r_markh = self.markH
        rckey = f"{row}:{col}"
        marked = not rckey in r_markh
        return marked

