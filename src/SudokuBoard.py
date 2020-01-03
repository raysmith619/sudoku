#SudokuBoard.pm

# Thanks to JCN for Tk reintroduction and insights.

# Sudoku Board Goals / Requirements
# 1. Runtime variable row, col, major rows, major cols
# 2. Runtime resize of puzzle board including text size
#    text resizes based on number of rows...
#
from tkinter import *
from tkinter.font import Font

from select_trace import SlTrace
from select_error import SelectError

import sudoku_globals as g

from SudokuData import SudokuData, CellDesc, CellMark

markerTagDef = 1         # Default marker tag
"""
Argument setting for create_line
"""
class LineArgs:
    pos = None          # orthogonal position
    args = []
    kwargs = {}

class SudokuBoard:
    pixelPerIn = 117       # Screen pixels per in (a guess)
    
    
    # Setup new board
    # Creates main window unless provided in opth{mw}
    def __init__(self,
            mw = None,
            frame = None,
            data = None,
            rows = None,        # Used only if data is None
            grows = None,
            cols = None,
            gcols = None,
            # TBD - determine via system call
            bdWidth = 3,            # Board with in inches
            bdHeight = 3,           # Board height in inches
            bdBg = "white",         # Board background
            bdBorderWidth = 6,      # Board border width
            bdBorderHeight = 6,     # Board border height
            bdBorderFg = "blue",    # Board border color
                                     # row, col, subrow, sub col from Data
            bdFont = None,
            bdFontName = "times",   # Board font name
                                       # Board fond size determined from row
        
            cellSep = 2,            # Cell separator in pixels
            cellSepFg = "skyblue",  # Cell separator color
            groupSep = 6,           # Cell group separator in pixels
            groupSepFg = "skyblue", # Group separator color
            hilightFg = "red",
            selectBg = "pink",
            markWidth = 4,          # Marker width
            markBg = "hotpink",      # Marker backround color
            initialData = None,
            ):
        
        # TBD - determine via system call
        self.bdWidth = bdWidth
        self.bdHeight = bdHeight
        self.bdBg = bdBg
        self.bdBorderWidth = bdBorderWidth
        self.bdBorderHeight = bdBorderHeight
        self.bdBorderFg = bdBorderFg
        # row, col, subrow, sub col from Data
        self.bdFont = bdFont
        self.bdFontName = bdFontName
        # Board fond size determined from row
        
        self.cellSep = cellSep
        self.cellSepFg = cellSepFg
        self.groupSep = groupSep
        self.groupSepFg = groupSepFg
        self.hilightFg = hilightFg
        self.selectBg = selectBg
        self.markWidth = markWidth
        self.markBg = markBg
        
        if data is not None:
            if rows is not None or grows is not None or cols is not None or gcols is not None:
                raise SelectError(f"Don't include data AND rows({rows}),"
                                  f"cols({cols}),grows({grows}),gcols({gcols})")
            rows = data.nRow
            grows = data.nSubRow
            cols = data.nCol
            gcols = data.nSubCol
        # Setup as empty cells, awaiting formatting marking info
        self.cells = [[CellDesc(row=ri+1, col=ci+1) for ci in range(cols)] for ri in range(rows)]
        if data is not None:
            rows = data.nRow
            grows = data.nSubRow
            cols = data.nCol
            gcols = data.nSubCol
            for ri in range(rows):
                row = ri + 1
                for ci in range(cols):
                    col = ci + 1
                    data_val = data.getCellVal(row=row, col=col)
                    if data_val is not None:
                        self.cells[ci][ri].val = data_val       # Set data value
        else:
            data = SudokuData(rows=rows, grows=grows, cols=cols, gcols=gcols)
        self.data = data        
            
        self.initialData = initialData
        if initialData is not None:
            self.initialize(initialData) 
        
        # Allow trace or traceList
        self.markH = {}        # Marked cells by tag (0 -> default)
        self.data = data        # Possibly empty
        
        
        # Uses mw if provided, else creates Minimal Tk setup
        if mw is None:
            mw = Tk()
            mw.title("Sudoku GUI")
        self.mw = mw
        self.frame = frame
        self.newBoard = 1
        # Finish Tk setup
        self.drawBoard()
        
        self.bindKeys()                    # Setup key event processing

    def addMark(self, tag=None, id=None, rc=None, col=None, row=None,
                  backColor=None, boundColor=None,
                  boundWidth=None, boundWidget=None):
        markH = self.markH
        if markH is None:
            raise SelectError("undefined markH")
        if tag not in markH:
            r_marks = markH[tag] = []  # new tag
        r_marks.append(CellMark(row=row, col=col, id=id, rc=rc,
                                backColor=backColor, boundColor=boundColor,
                                boundWidth=boundWidth, boundWidget=boundWidget))

    def initialize(self, initialData):
        """ initialize - TBD
        """
        pass
    
        
        
    # Setup key event processing
    def bindKeys(self):
        mw = self.mw
        mw.bind(0, self.key_digit) 
        mw.bind(1, self.key_digit) 
        mw.bind(2, self.key_digit) 
        mw.bind(3, self.key_digit) 
        mw.bind(4, self.key_digit) 
        mw.bind(5, self.key_digit) 
        mw.bind(6, self.key_digit) 
        mw.bind(7, self.key_digit) 
        mw.bind(8, self.key_digit) 
        mw.bind(0, self.key_digit) 
    
    
    def key_event(self, event):
        """ Process key events not bound elsewhere
        """
        SlTrace.lg(f"key_event {event}", "key_event")
        
    # Get selected cells
    def getSelected(self):
        r_mk = self.getMarked()
        if r_mk is None or len(r_mk) == 0:
            return None 
    
        return r_mk
    
    
    
    def keyDown(self):
        r_c  = self.getSelected()
        if r_c is None:
            return 
        
        row = r_c.row
        col = r_c.col
        if row < self.data.nRow:
            row += 1             # Stop at last
        self.selectCell(row, col)
    
    
    
    def keyLeft(self):
        r_c  = self.getSelected()
        if r_c is None:
            return 
        
        row = r_c.row
        col = r_c.col
        if col > 1:
            col -= 1             # Stop at first
        self.selectCell(row, col)
    
    
    
    def keyRight(self):
        r_c  = self.getSelected()
        if r_c is None:
            return 
        
        row = r_c.row
        col = r_c.col
        if col < self.data.nCol:
            col += 1             # Stop at first
        self.selectCell(row, col)
    
    
    
    def keyUp(self):
        r_c  = self.getSelected()
        if r_c is None:
            return 
        
        row = r_c.row
        col = r_c.col
        if row > 1:
            row -= 1             # Stop at first
        self.selectCell(row, col)
    
    
    
    def keySpace(self):
        r_c  = self.getSelected()
        if r_c is None:
            return 
        
        row = r_c.row
        col = r_c.col
        col += 1
        if (col > self.data.nCol):
            col = 1
            row += 1
            if row > self.data.nRow:
                row += 1
                if row > self.data.nRow:
                    row = 1 
            
        self.selectCell(row, col)
      
    
    # Key processing functions
    def key_digit(self, event):
        key = ord(event.char) - ord('0')
        r_mk = self.getSelected()       # Only get first
        if r_mk is None or len(r_mk) == 0:
            SlTrace.lg("Nothing selected")
            return
        
        r_c = r_mk[0]
        row = r_c.row
        col = r_c.col
        self.setCell(row, col, key)
    
    
    # Clear markers
    def clearMarks(self, tag=None):
        if tag is None:
            tag = markerTagDef    # Do default marker
        markH = self.markH
        r_marks = markH[tag] if tag in markH else None
        if r_marks is None:
            return 
        
        cv = self.cv
        for r_m in r_marks:
            cv.delete(r_m.id)
        
        del markH[tag]
    
    
    
    # Clear all marks
    def clearMarksAll(self):
        markH = self.markH
        if markH is None:
            return 
        
        for tag in markH:
            self.clearMarks(tag)
    
    
    # Board clicked
    def click_board(self, event):
        SlTrace.lg(f"clickBoard {event}")
        r_c = self.getClickedCell(event)
        if r_c is None:
            return 
        row = r_c.row
        col = r_c.col	
        SlTrace.lg(f"click row={row} col={col}", "any")
        if (self.isSelected(row, col)):
            self.clearMarks()
        else:
            self.selectCell(row, col)
     
      
    
    # Set options when found in kwargs
    # Checks kwargs for all settings found in r_def hash
    # If option key is found in %opth that option key is set in r_set
    # r_def and r_set may be the same, e.g. self
    def setOpts(self, r_def, **kwargs):
        for key in kwargs:
            opt = kwargs[key]
            if opt is not None:
                setattr(self, key, opt) # ??? TBD is this wrong???
    
    
    
    def destroy(self):
        """ Destroy board
        TBD - this does not get board off the window
        """
        cv = self.cv
        if cv is not None:
            cv.destroy()
            self.cv = None
        if self.frame is not None:
            self.frame.destroy()
            self.frame = None

    def display(self, msg=None):
        if msg is None:
            msg = "board display"
        if self.data is not None:
            self.data.display(msg=msg)
        else:
            SlTrace.lg(f"{msg} - no data")
    
    # Get data cell
    def getCell(self, row=None, col=None):
        ri = row - 1
        ci = col - 1
        return self.cells[ci][ri]
    
    # Get data cell
    def getCellVal(self, row=None, col=None):
        cell = self.getCell(row=row, col=col)
        return cell.val
    
    
    # 
    def setCell(self, row=None, col=None, val=None,
                x1=None, y1=None, x2=None, y2=None):
        """ Set cell to values, display value if present
        Data is updated if present
        """
        if col is None:
            raise SelectError(f"setCell: Missing column")
        if col is None:
            raise SelectError(f"setCell: Missing row")
        if col < 1 or col > self.data.nCol:
            raise SelectError(f"setCell column({col} out of bounds(1-{self.data.nCol})")
        if row < 1 or col > self.data.nRow:
            raise SelectError(f"setCell column({row} out of bounds(1-{self.data.nRow})")
        r_c = self.getCell(row=row, col=col)
        if r_c is None:
            raise SelectError(f"No cell at row={row} col={col}")
        
        if x1 is not None:
            r_c.x1 = x1
        if x2 is not None:
            r_c.x2 = x2
        if y1 is not None:
            r_c.y1 = y1
        if y2 is not None:
            r_c.y2 = y2
            
        cell_val_id = r_c.valId
        cv = self.cv
        data = self.data
        if (data is not None):
            if val is not None:
                data.setCellVal(row, col, val)    # Update data
        
        if cell_val_id is not None:
            cv.delete(cell_val_id)
        # add new character
        rowSize = self.rowSize
        font_size = -(rowSize-1)       # A bit shorter than cell
        if self.isEmpty(val):
            cell_disp = " "      # Empty
        else:
            if isinstance(val, int):
                cell_disp = f"{val}"
            else:
                cell_disp = val
            
        opts = {'text' : cell_disp}
        opts['font'] = Font(name=self.bdFontName, size=font_size, exists=False)
        x = (r_c.x1 + r_c.x2)/2
        y = (r_c.y1 + r_c.y2)/2
        
        r_c.valId = cv.create_text([x, y], opts)
    
    
    def drawBoard(self):
        if self.data is None:
            SlTrace.lg("no data to draw")
            return
        
        top_frame = self.mw     # Default
        if self.frame is not None:
            top_frame = self.frame      # Place inside frame
        ppi = self.pixelPerIn
        bdWidth = self.bdWidth
        width = bdWidth*ppi
        bdHeight = self.bdHeight
        height = bdHeight*ppi
        bdBg = self.bdBg
        
        bdBorderWidth = self.bdBorderWidth
        bdBorderHeight = self.bdBorderHeight
        xmin = self.xMin = bdBorderWidth
        xmax = self.xMax = width - xmin
        ymin = self.yMin = bdBorderHeight
        ymax = self.yMax = height - ymin
        
        
        f1 = Frame(top_frame)
        f1.pack(expand = 0, fill = "x")
        f2 = Frame(top_frame)
        f2.pack(expand = 1, fill = "both")
        cv = Canvas(f2, width = width,
        	       height = height,
        	       bg = bdBg)
        cv.pack()
        self.cv = cv
        
        # Create a box for clicking
        cv.create_rectangle([0, 0,
        	       width, height],
        	       fill = bdBg,
        	       tags = "click")
        cv.bind("<Button-1>", self.click_board)
        
        
        # create cells and group lines
        self.drawCells()
        
        # Create Board surrounding border
        box_args = []
        box_args.append([xmin, ymin, xmax, ymax])
        box_kwargs = {}
        box_kwargs['width'] = self.bdBorderWidth
        box_kwargs['outline'] = self.bdBorderFg
        cv.create_rectangle(box_args, box_kwargs)
        top_frame.update()
    
    
    
    # Draw cells and grouping lines
    def drawCells(self):
        global Initial_data
        
        cv = self.cv
        xmin = self.xMin
        xmax = self.xMax
        ymin = self.yMin
        ymax = self.yMax
        
        # Separator line attributes
        # (Canvas createLine)
        cell_opt_h = {'width':self.cellSep,
        	    'fill':self.cellSepFg}
        
        group_opt_h = {'width':self.groupSep,
        	    'fill':self.groupSepFg}
    
        row_lines = self.getDividers(type="row",
        			     cell=self.data.nRow, group=self.data.nSubRow,
        			     min=ymin, max=ymax,
        			     cellOpt=cell_opt_h,
        			     groupOpt=group_opt_h)
        
        
        col_lines = self.getDividers(type="col",
        			     cell=self.data.nCol, group=self.data.nSubCol,
        			     min=xmin, max=xmax,
        			     cellOpt=cell_opt_h,
        			     groupOpt=group_opt_h)
        
        rowSize = self.rowSize
        colSize = self.colSize
        
        # Setup board font
        mw = self.mw
        bdFont = Font(family=self.bdFontName,
        		       size=(colSize-1))
        self.bdFont = bdFont
        # Setup cells for data display, selection
        Initial_data = self.initialData
        
        # TBD: Set up clickCell to obtain entry from event position
        for ri in range(len(row_lines)):
            row = ri+1
            r_l1 = row_lines[ri].args      # [x1,y1,x2,y2]
            y1 = r_l1[1]
            y2 = y1 + rowSize
            for ci in range(len(col_lines)):
                col = ci+1
                c_l1 = col_lines[ci].args      # [x1,y1,x2,y2]
                x1 = c_l1[0]
                x2 = x1 + colSize
                if row <= self.data.nRow and col <= self.data.nCol:
                    self.setCell(row=row, col=col, x1=x1, y1=y1, x2=x2, y2=y2)
                '''
                if self.initialData is not None:
                    orig_val = self.initialData.getCell(row, col)
                    if orig_val is not None:
                        self.markCell(row=row, col=col, tag='origData',
                            add=1,
                            boundWidth='NONE', boundColor='NONE',
                            backColor="gray90")
                '''
    
        # Mark squares 
        for r_line in row_lines:
            cv.create_line(r_line.args, r_line.kwargs)
        
        for r_line in col_lines:
            cv.create_line(r_line.args, r_line.kwargs)
    
    
    
    def getData(self, ):		# Returns: data
        return self.data
    
    
    
    def getDividers(self, type=None,
                        cell = None,
                        group = None,
                        min = None,
                        max = None,
                        cellOpt = None,
                        groupOpt = None,
                    ):
        """ Get divider lines
        Returns array of create_line options
        sets rowSize/colSize (pixels) appropriately
        sets pos in returned lines

        :returns: array of canvas line args
        """
        if type is None or (type != "row" and type != "col"):
            raise SelectError(f"bad type:{type}")
        if cell is None:
            raise SelectError("cell missing")
        if group is None:
            raise SelectError("group missing")
        if min is None:
            raise SelectError("min missing")
        if max is None:
            raise SelectError("max missing")
        if cellOpt is None:
            raise SelectError("cellOpt missing")
        if groupOpt is None:
            raise SelectError("groupOpt missing")
        
        lines = []                 # Array of refs to line args
        cell_size = int((max-min)/cell)
        if (type == "row"):
            self.rowSize = cell_size
        else:
            self.colSize = cell_size
        
        
        xmin = self.xMin
        ymin = self.yMin
        xmax = self.xMax
        ymax = self.yMax
        for i in range(cell):
            is_group = False      # True if group divider
            is_group = True if i % group == 0 else False
            val = min + i*cell_size  # combersome, but reduces
                                            # trunk error
            # TBD adjust for border overlap


                
            lineargs = LineArgs()                          # Staging area for create_line args
            if type == "row":
                x1 = xmin
                x2 = xmax
                y1 = y2 = val                     # horizontal line
            else:
                y1 = ymin
                y2 = ymax
                x1 = x2 = val                     # vertical line
            lineargs.pos = val                      # Line position(orthogonal)
            lineargs.args = [x1, y1, x2, y2]
            
            if is_group:
                lineargs.kwargs = groupOpt
            else:
                lineargs.kwargs = cellOpt
            lines.append(lineargs)
            
        return lines
    
    
    
    
    def rowColRef(self, row, col):                 # 
        """ Translate row, col to cell ref
        :row:
        :col:
        :returns: ref to cell
        """
        return self.cells[col-1][row-1]
    
    
    
    def getClickedCell(self, ev):                    # Returns: cell ref, else None
        """ Get clickec cell
        :ev: button clikc event
        :returns: ref to cell
        """
        cv = self.cv
        xMin = self.xMin
        yMin = self.yMin
        x = ev.x
        y = ev.y
        if SlTrace.trace("any"):
            ev_x = ev.x
            ev_y = ev.y
            SlTrace.lg(f"getClickedCell: ev_x:{ev_x} ev_y:{ev_y}"
              + f" x={x} y={y} xMax={self.xMax} yMax={self.yMax}")
    
        if (x < 0 or y < 0
                or x > self.xMax or y > self.yMax):
            return None 
        
        rowSize = self.rowSize
        colSize = self.colSize
        if rowSize <= 0 or colSize <= 0:
            return None
        
        ri = int(y/colSize)
        ci = int(x/rowSize)
        cells = self.cells
        if cells is None:
            return None 
        
        return cells[ri][ci]
    
    
    
    #
    def getMarked(self, tag=None):
        """ Get marked cell(s)
        :returns: array of refs to marked cells
        """
        if tag is None:
            tag = markerTagDef 
    
        markH = self.markH
        if markH is None or tag not in markH:
            return []
        
        r_marks = markH[tag]
        if r_marks is None:
            return []
         
        return r_marks
    
    
    
    # Check if cell is selected
    def isSelected(self, row, col):         # Returns: true iff selected
        r_m = self.getMarked()
        if r_m is None or len(r_m) == 0:
            return False
        
        r_c = r_m[0] 
        if r_c is None:
            return False
         
        if r_c.row == row and r_c.col == col:
            return True
         
        return False
    
    
    # 
    def markCell(self, col=None, row=None, tag=None,
                  add=None, backColor=None, boundColor=None, boundWidth=None, boundWidget=None):
        """ Mark cell
        Does not select cell
        col, row, [tag, add,
        backColor, boundColor,
        boundWidgt
        """
        if col is None:
            raise SelectError("markCell no col")
        if row is None:
            raise SelectError("markCell no row")
        
        if add is None:
            add = False             # Add to tagged group, else delete prev
        if tag is None:
            tag = markerTagDef             # tag grouping, default
        
        r_c = self.rowColRef(row, col)
        args = [r_c.x1, r_c.y1, r_c.x2, r_c.y2]
        kwargs = {}
        if backColor is not None:
            kwargs['fill'] = backColor
        if boundWidth is not None:
            kwargs['width'] = boundWidth
        if boundColor is not None:
            kwargs['outline'] = boundColor 
        cv = self.cv
        mark_id = cv.create_rectangle(*args, **kwargs)
        if not add:
            self.clearMarks(tag) 
        self.addMark(tag=tag, id=mark_id, rc=r_c, col=col, row=row,
                  backColor=backColor, boundColor=boundColor,
                  boundWidth=boundWidth, boundWidget=boundWidget)
    
    
    
    # Select cell
    # Marks cell
    # Unselects previously selected
    def selectCell(self, row, col):              # Returns: ref to cell 
        r_c = self.rowColRef(row, col)
        if r_c is None:
            return None
        
        self.markCell(row=row, col=col)
        return r_c
        
        
        
    def showData(self, data=None):
        new_data = True if data is not None else False
        if data is None:
            data = self.data
        
        if not isinstance(data, SudokuData):
            raise SelectError(f"Warning -- method add_data({type(data)}) expects a 'SudokuData' object")
            return
        
        self.clearMarks()
        ###new_board = self.newBoard
        for nr in range(1, self.data.nRow+1):
            for nc in range(1, self.data.nRow+1):
                new = data.getCellVal(row=nr, col=nc)
                ###old = self.getCell(nr, nc) or ""
                self.setCell(nr, nc, new)
        if SlTrace.trace("show_data"):
            SlTrace.lg("show_data")
            self.display()
    
    
    
    # Check if value considered  empty
    def isEmpty(self, val):
        return self.data.isEmpty(val)
