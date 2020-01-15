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
from sudoku_vals import SudokuVals, CellDesc

    
        
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
    
    @classmethod
    def data2vals(cls, data):
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
    
    @classmethod
    def vals2data(cls, sval):
        """ Convert SudokuVals to SukokuData
        :sval: SudokuVals
        :Returns: SudokuData
        """
        sd = SudokuData(rows=sval.nRow, grows=sval.nSubRow,
                        cols=sval.nCol, gcols=sval.nSubCol)
        for nr in range(1, sval.nRow+1):
            for nc in range(1, sval.nCol+1):
                val = sval.getCellVal(row=nr, col=nc)
                if val is not None:
                    sd.setCellVal(row=nr, col=nc, val=val)
        return sd                

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
        if base is not None:
            self.vals = self.data2vals(base)
        else:
            self.vals = SudokuVals(rows=rows, grows=grows, cols=cols, gcols=gcols)
    
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
        self.vals.clear()
    
    
    # Clear sell
    def clearCell(self, row=None, col=None):
        self.vals.clearCell(row=row, col=col)

    def copy(self):        # Returns: deep copy
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
        if msg is None:
            msg = "SudokuData"
        self.vals.display(msg=msg)

    def setCell(self, row=None, col=None, val=None):
        """ Set cell value
        :returns: updated cell
        """
        ret = self.vals.setCell(row=row, col=col, val=val)
        if not self.isValid():
            SlTrace.lg(f"setCell: row={row}, col={col}, val={val} not valid")
            self.display("Invalid arrangement")
            SlTrace.lg("by rows")
            for ri in range(self.nRow):
                nr = ri + 1
                SlTrace.lg(f"row:{nr} vals:{self.getRowVals(nr, include_nones=True)}")
            SlTrace.lg("by columns")
            for ci in range(self.nCol):
                nc = ci + 1
                SlTrace.lg(f"col:{nc} vals:{self.getColVals(nc, include_nones=True)}")
            self.display("After listing")
            raise SelectError("Invalid arrangement")
        
        return ret
    
    def isValid(self):
        """ Check for valid arrangement
        """
        return self.vals.isValid()
         
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
        return self.vals.getLegalVals(row=row, col=col)
    
    
    
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
                if SlTrace.trace("empty"):
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
        if val is None or (isinstance(val, str) and val == "0") or val == 0:
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
    
    #
    def getSq3Vals(self, row=None, col=None):
        """ Get valuse in sub-by-sub square
        :Returns: col values
        """
        sq3_vals = self.vals.getSq3Vals(self, row=row, col=col)
        return sq3_vals

    def getColVals(self, col=None, include_nones=None):
        """ Get values in given row
        :row: column number
        :include_nones: True - include Nones in list 
        :Returns: values in row 
        """
        return self.vals.getColVals(col=col, include_nones=include_nones)

    def getRowVals(self, row=None, include_nones=None):       # Returns: row values
        """ Get values in given row
        :row: column number
        :include_nones: True - include Nones in list 
        :Returns: values in row 
        """
        return self.vals.getRowVals(row=row, include_nones=include_nones)

    
    def setCellVal(self, row=None, col=None, val=None, quiet=False):
        """ set Sudoku cell with value - may be EMPTY
          :row:          1-nRow
          :col:          1-nCol
          :val:          EMPTY, 1-9, marking value
          :quiet:        1 -> no trace, no cell change
        """
        self.vals.setCellVal(row=row, col=col, val=val)
        
        if not quiet:               # quiet -> move invisibly also
            SlTrace.lg(f"setCellVal(row:{row}, col:{col}, val:{val})", "any")
        
        self.curRow = row
        self.curCol = col
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
        val = self.vals.getCellVal(row=row, col=col)
        
        return CellDesc(row=row, col=col, val=val)
    
    
    # Get data cell
    def getCellVal(self, row=None, col=None):
        return self.vals.getCellVal(row=row, col=col)
    
    # Assemble list of next move choices
    # sorted in ascending number of values per cell
    def getChoices(self):       # Returns: ref to sorted array of choices
        return self.vals.getChoices()
    
    def orderChoices(self, cells):
        """
        :cells:  List of cells
        :returns: ref to sorted array of choices 
                           # to be ordered in increasing
                            # number of values
        """
        return self.vals.orderChoices(cells)                            
    
    # Get list of non-empty cells
    def getNonEmptyCells(self):      # Returns: array of {row=, col=}
        return self.vals.getNonEmptyCells()
    
    
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

