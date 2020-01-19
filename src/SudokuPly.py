#SudokuPly.pm
"""
One play possibilities
"""
from select_trace import SlTrace
from select_error import SelectError
from sudoku_search_stop import SudokuSearchStop
import sudoku_globals as g

from SudokuData import SudokuData, CellDesc
from docutils.nodes import row
    
class SudokuPly(SudokuData):
    ch_one_depth = None     # Depth in choice 0
    stop_searching = False        # Set True to stop searching (soon)
    
    
    
    # Setup move display
    @classmethod
    def setDisplay(cls, display_rtn=None, display_time=None):
        if display_time is None:
            display_time = .3 
        cls.DisplayRtn = display_rtn
        cls.Display_time = display_time

    @classmethod
    def clear_search_stop(cls):
        cls.stop_searching = False

    @classmethod
    def stop_search(cls, msg=None):
        cls.stop_searching = True
    
    @classmethod
    def ck_search(cls):
        if cls.stop_searching:
            raise SudokuSearchStop()
        
    def __init__(self,displayRtn=None, displayTime=None, **kwargs):
        if SlTrace.trace("sudokuply"):
            SlTrace.lg(f"\nSudokuPly(kwargs={kwargs}")
        self.ck_search()
        self.choices = None
        self.setCellList = []        # setCell trace
        if displayRtn is not None:
            self.DisplayRtn = displayRtn
        if displayTime is not None:
            self.DisplayTime = displayTime
        self.level = 0
        self.depth = 0
        super().__init__(**kwargs)
        self.startList = None
        base = kwargs['base'] if 'base' in kwargs else None
        if SlTrace.trace("sudokuply"):
            if base is not None:
                base.display("SudokuPly(base)")
        self.setPlyData(base=base)
        self.choices = self.getChoices()
    
    
    #
    # Populate puzzle
    # - populate given cells
    # 
    def populatePuzzle(self, **kwargs):
        """ Populate puzzle
        populate given cells
        :startLis: t=><start array of cells>
        :choice:=><index in startList for prospective cell>
        :returns: array of fully populated bds
        """
        self.ck_search()
        startList=None
        if 'starList' in kwargs:
            startList = kwargs['starList']
        choice=None
        if 'choice' in kwargs:
            choice = kwargs['choice']
        self.level += 1
        if startList is None:
            SlTrace.lg(f"popuatePuzzle(level:{self.level}): no startList")
            startList = []
        startCells = startList[:]        
        if (SlTrace.trace('depth')):
            SlTrace.lg(f"populatePuzzle: level={self.level}"
                    + f" depth = {self.depth}")
            self.display("end populatePuzzle")
            SlTrace.lg(f"================")
    
        
        if len(startCells) == 0:
                                # Check if solution possible
                                # and unique
            sols = self.solvePuzzle(nFirst=10)
            self.level -= 1
            return sols
    
        
        if choice is not None:
            r_choice = startCells.pop(choice)
            r_chvals = r_choice.vals
            chvals = r_chvals
            for chval in chvals:
                ply = self.copy()
                row = r_choice.row
                col = r_choice.col
                ply.setCell(row, col, chval)
                ply.new_move()
                
                del kwargs['choice']        # Look for choices
                sols = ply.populatePuzzle(**kwargs)
                if sols == 0:
                    continue
                
                self.level -= 1
                return sols
    
            self.level -= 1
            return []        # No acceptable patterns
    
        
        choices = self.orderChoices(startCells)
        choices = choices[:]
        if (len(choices) == 0):
            self.level-= 1
            return []
    
        
        ncmin = choices[0].nval
        if ncmin == 0:
            self.level -= 1
            return []        # No choices for most constrained
    
        maxind = len(choices) - 1
        r_max = choices[maxind]    # Look at least constrained
        
        r_chvals = r_max.vals
        chvals = r_chvals[:]
        for chval in chvals:
            sols = self.populatePuzzle(
                        startList=choices,
                        choice=maxind,
                        )
            if sols == 0:
                continue
            self.level -= 1
            return sols
    
        self.level -= 1
        return []
    
    
    
    #
    # Set current ply data
    def setPlyData(self, base=None):
        if SlTrace.trace("setPlyData"):
            self.display(f"setPlyData before depth={self.depth} choices={self.choices}")
        if base is None:
            self.choices = []  # Cell choices ordered by number of vals
            self.nchoice = 0   # Number of choices
            self.depth = 0
            self.data = None
        if isinstance(base, SudokuPly):
                self.back = base                        # link back
                ###r_base_data = base.data
                ###self.data = SudokuPly(base=r_base_data)
                a_start_list = base.startList
                a_new_list = self.startList = []
                depth = self.depth
                if base is not None:
                    depth = base.depth
                if depth is None:
                    depth = 0 
                self.depth = depth + 1
                if base.level is not None:
                    self.level = base.level
                        
                if a_start_list is not None:
                    a_new_list.extend(a_start_list)
        elif isinstance(base,SudokuData):
                pass
                ###self.data = SudokuData(base=base)
        else:
                raise SelectError(f"Can't set SudokuPly from {base}")

        self.choices = self.getChoices()
        if SlTrace.trace("setPlyData"):
            self.display(f"setPlyData after depth={self.depth} choices={self.choices}")
    
    # Get cell info
    def getCell(self, row, col):       # Returns: data cell
        cell = self.vals.getCell(row, col)
        return cell
    
    
    
    # Get base data (SudokuData)
    # or new data with partial subset
    def getData(self, data=None, subset=None):       # Returns: SudokuData
        subset = subset
        if data is None:
            data = self.data
        if subset is None:
            return data
        
        new_data = data()
        for cell in subset:
            row = cell.row
            col = cell.col
            val = data.getCell(row, col)
            new_data.setCellVal(row=row, col=col, val=val)
    
        return new_data
    
    
    
     
    
    # get links to all ply ancestors
    def getPlyList(self):    # Retrns: List of plys, including this
        plys = []
        back = self
        while back is not None:
            plys.append(back)
            back = back.back
    
        return plys
    
        
    def getSetList(self):    # Returns: list of setCell hash
        plys = self.getPlyList()
        sets =  []
        for ply in plys:
            setCellList = self.setCellList
            sets.append(setCellList)
        return sets
    
    
    #
    # Make puzzle setup
    #
    def makePuzzle(self, *args, **kwargs):    # Returns: ply with sol else None
        """
        :startList: <start array of cells>
        :choice: <index in startList for prospective cell>
        """
        startList = None
        if 'startList' in kwargs:
            pops = self.populatePuzzle(*args, **kwargs)
            startList = kwargs['startList']
        if startList is None:
            raise SelectError("makePuzzle: undefined startList")
                
                

        if len(pops) == 1:
            return pops[0]
    
        return None
    
    
    # Assemble list of next move choices
    # sorted in ascending number of values per cell
    @staticmethod
    def _choices_cmp_val(elm):
        return elm.nval
    
    ''' inherited from SudokuData
    # Get next empty cell in board data, if any
    def getNextEmpty(self, ):      # Returns: cell ref, else None if none empty
        r_data = self.data
        return r_data.getNextEmpty()
    '''
    
    def getNextChoice(self):
        """ Get next suggested cell
        going through start list, choices till best choice in start list
        then best choice, till done then empty
        for now we check for empty
        """
        if SlTrace.trace("getnextchoice"):
            self.display("getNextChoice")
        self.choices = self.vals.getChoices()
        if SlTrace.trace("getnextchoice"):
            SlTrace.lg(f"getNextChoice of {self.choices}")
        start_list = self.startList
        choices = self.choices
        if choices is None or len(choices) == 0:
            return None
        
        ch = self.choices[0]
        if ch is None or len(ch.vals) == 0:
            return None        # No choice for most constrained
            
        if (start_list is None
                or len(start_list) == 0):        # No start -> take choice
            return self.choices.pop(0)
    
        # Choose choice specified in start_list    
        for ich in range(choices):
            choice = choices[ich]
            ch_row = choice.row
            ch_col = choice.col
            for ist in range(len(start_list)):
                start = start_list[ist]
                if (start.row == ch_row
                    and start.col == ch_col):
                    start_list.pop(ist)
                    self.choices.pop(ich)
                    return choice
    
        
        return None
    
    
    #
    # Set new ply as deep copy of old ply
    # Set from arg's data
    # This may be opdimized later
    def setPly(self, r_ply):
        r_data = r_ply.data
        self.setData(r_data)
    
    
    
    # Set puzzle start up values
    #
    def setPuzzle(self, **kwargs):        # Returns: TRUE iff successful setup
                    #startList= list of cells to populate
        if "startList" not in kwargs:
            raise SelectError("missing startList")
        starts = kwargs["startList"]
        # Process until list completed
        while starts > 0:
            pass
    
    def solveChoice(self, *args, **kwargs):      # Returns: solution list, empty if none
        """ Solve puzzle for given choice
        If no choice - use first in 'choices'
        Plan
        Check for possible solutions by keeping a list of cells ordered
        by increasing number of legal values.
        Loop over candidates in choice
            Choose candidate  value from cell
            Solve resulting board
            returning list of solutions, possibly empty
        """
        if SlTrace.trace("solvechoice"):
            SlTrace.lg(f"solveChoice: args={args} kwargs={kwargs}")
            self.display()
        if self.getNextEmpty() is None:
                            # Filled
            if self.DisplayRtn is not None:
                self.DisplayRtn()
    
            return [self]
    
    
        choice = kwargs['choice'] if 'choice' in kwargs else None # choice CellDesc
        nfirst = kwargs['first'] if 'first' in kwargs else None          # Limit to first n if defined
        start_list = kwargs['startList'] if 'startList' in kwargs else None
        # Add selection restrictions, if any
        if start_list is not None:
            if not hasattr(self, 'startList'):
                self.startList = [] 
            self.startList.append(start_list)
            
        if choice is None:
            choice = self.getNextChoice()
            if choice is None:
                return [] 
        if SlTrace.trace("solvechoice"):
            SlTrace.lg(f"solveChoice: choice={choice} nfirst={nfirst} start_list={start_list}")
            self.display()
    
        sols = []            # list of solutions, possibly empty
        row = choice.row
        col = choice.col
        vals = choice.vals
        
        for val in vals:
            legals = self.getLegalVals(row=row, col=col)
            if len(legals) < 1:
                SlTrace.lg(f"solveChoice {kwargs} - len(legals)<1")
                legals = self.getLegalVals(row=row, col=col)
                continue
            if val not in legals:
                SlTrace.lg(f"val{val} not in row={row} col={col} legals:{legals}")
                continue
            sol1s = self.solveChoiceOne(row=row, col=col, val=val,
                           first=nfirst-len(sols))
            sols.extend(sol1s)
            if len(sols) >= nfirst:
                break          # Quit if we got enough
    
        return sols
       
    
    
    # 
    def solveChoiceOne(self, **kwargs):
        """ Solve puzzle for one specific row, col, value
        Returns: list of solutions, possibly empty
        """
        row = kwargs['row']
        col = kwargs['col']
        val = kwargs['val']
        nfirst = kwargs['first']
        self.enterChoiceOne(**kwargs)
        ch1 = SudokuPly(base=self)   # Create deep copy of ourself
        legals = self.getLegalVals(row=row, col=col)
        if len(legals) < 1:
            SlTrace.lg(f"solveChoiceOne {kwargs} - len(legals)<1")
            legals = self.getLegalVals(row=row, col=col)
        else: 
            ch1.setCell(row, col, val)
            ch1.new_move()
        ret = ch1.solveChoice(first=nfirst)
        self.exitChoiceOne(ret)
        return ret
       
    
    
    #
    # Deep copy of ply
    #
    def copy(self, ):        # Returns: deep copy
        ply = SudokuPly(base=self)
        return ply
        
    
    
    # Simple display of data area
    def display(self, msg=None):
        if msg is None:
            msg = "SudokuPly data"
        super().display(msg=msg)
    
    
    
    def displaySetCellList(self, ):
        setCells = self.getSetList()
        SlTrace.lg(f"setCells:", "display")
        for r_set in setCells:
            col = r_set.col
            row = r_set.row
            val = r_set.val
            SlTrace.lg(f"C{col}R{row}:{val}", "display")
    
        SlTrace.lg(f"")
    

    def enterChoiceOne(self, row=None, col=None, val=None, first=None):
        if self.ch_one_depth is None:
            self.ch_one_depth = 0 
        self.ch_one_depth += 1
        if SlTrace.trace("solve"):
            SlTrace.lg(f"enterChoiceOne depth: {self.ch_one_depth}"
                + f" row={row} col={col} val={val}")
            self.display()
    
        if self.Display_time is not None and self.DisplayRtn is not None:
            self.DisplayRtn()
    
    
    def exitChoiceOne(self, res=None):
        if self.ch_one_depth is None:
            self.ch_one_depth = 0 
        self.ch_one_depth -= 1
        if SlTrace.trace("solve"):
            SlTrace.lg(f"exitChoiceOne depth: {self.ch_one_depth}")
            self.display()
    
    
    def solvePuzzle(self, startList=None, nFirst=1):      # Returns: ref to solution, else None
        return self.solveChoice(first=nFirst)


    def new_backup(self):
        """ Track moves
        """
        if self.puzzle is not None:
            self.puzzle.new_backup(self)

    def new_move(self):
        """ Track backups
        """
        if self.puzzle is not None:
            self.puzzle.new_move(self)
