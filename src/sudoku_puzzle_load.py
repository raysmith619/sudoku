# sudoku_puzzle_load.py
"""
Support for the loading of sudoku puzzle specification
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
     """
import sys, traceback

from select_trace import SlTrace
from select_error import SelectError
from SudokuPuzzle import SudokuPuzzle

# Added to between any prefix and the compile string if trace: "puzzle_load" flag is set
test_prefix = """
print("dir: ", dir())
print("globals: ", globals())
print("locals: ", locals())
""" 

class SudokuPuzzleLoad:
    """ Support simple puzzle building commands
        puzzle(rows=..., cols=..., desc=description)
        row(cols number of values, 0/None for empty)
    """
    @classmethod
    def set_input(cls, pfile=None, pstr=None):
        """ Setup file access
        :pfile: file name/stream containing puzzle specification
            OR
        :pstr: string containing puzzle specification
        :returns: class instance
        """
        cls.file_name = None        # Set to name if known
        cls.puzzle_string = pstr
        if pfile is not None and pstr is not None:
            raise SelectError(f"Only one of pfile({pfile}) or pstr({pstr}) may be specified")
        
        if pfile is not None:
            if isinstance(pfile, str):
                cls.file_name = pfile
                try:
                    fin = open(pfile)
                except Exception as ex:
                    SlTrace.lg(f"open puzzle file {pfile} failed {str(ex)}")
                    return None
            else:
                fin = pfile         # Input is an opened stream    
            try:
                pstr = fin.read()
                fin.close()
            except Exception as ex:
                SlTrace.lg(f"input read {pfile} failed {str(ex)}")
                return cls

        cls.puzzle_string = pstr
        cls.cur_row = 0
        return cls
    
    @classmethod
    def file2puzzle(cls, file, prefix=None):
        """ Take file name/object and return SudokuPuzzle
        :file: file name/path / open stream
        :prefix: optional string to prefix file text
        """
        spl = cls.set_input(pfile=file)
        puzzle = spl.procCmdString(prefix=prefix)
        return puzzle
        

    @classmethod
    def get_puzzle(cls):
        """ Retrieve puzzle complete or in progress
        """
        return cls.sudoku_puzzle
    
    @classmethod
    def procCmdString(cls, string=None, prefix=None):
        """ Process python code string, with prefix text
        :string: input string
        :prefix: optional string to prefix code string for compile
        :Returns: resulting cls 
        """
        cls.result = False          # Set True if OK
        if string is None:
            string = cls.puzzle_string
        if string is None:
            raise SelectError("string is missing")
        
        gbls = {'version' : cls.version,
                'puzzle' : cls.puzzle,
                'row' : cls.row,
                'end_puzzle' : cls.end_puzzle
                }
        
        compile_str = ""
        if prefix is not None:
            compile_str = prefix
            if not prefix.endswith("\n"):
                compile_str += "\n"         # Insure ending newline
        if SlTrace.trace("puzzle_load"):
            compile_str += test_prefix
        compile_str += string
        compile_str += "\nend_puzzle()\n"   # End puzzle
        try:
            exec(compile_str, gbls)
            cls.result = True
            return cls.sudoku_puzzle
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            SlTrace.lg(f"Error while executing text from {cls.file_name}\n    {str(e)}")
            inner_cmds = False
            for tbfr in tbs:  # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                if False:       # TFD
                    inner_cmds = True
                    SlTrace.lg("    --------------------")  # show bottom (in dots_commands.py)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            cls.result = False
        
        raise SelectError("compile error")


        
                
    """
    Basic game file loading functions
    Generally one per file command
    """
    
    @classmethod
    def version(cls, version_str):
        cls.version_str = version_str
        
    @classmethod
    def puzzle(cls, desc=None,
                rows=None, grows=None, cols=None, gcols=None):
        """ Start processing of puzzle
        :returns:  False if not processing this game
        """
        SlTrace.lg(f"puzzle(desc={desc}, rows={rows}, grows={grows} cols={cols} gcols={gcols})")
        cls.desc = desc 
        cls.rows = rows
        cls.grows = rows
        cls.cols = cols
        cls.gcols = gcols 
        cls.cur_row = 0
        cls.sudoku_puzzle = SudokuPuzzle(desc=desc, rows=rows, grows=grows, cols=cols, gcols=gcols)
        if SlTrace.trace("puzzle_load"):
            cls.sudoku_puzzle.display("puzzle() start")
        
    @classmethod    
    def row(cls, *col_vals):
        """ Add next rows of valuse
        :col_vals: column values for this row
            Each argument is either:
                a 0/None for empty square
                OR
                a value between 1 and cls.cols
        """
        global sudoku_puzzle
        
        cls.cur_row += 1
        if cls.cur_row > cls.rows:
            raise SelectError(f"row(cls.cur_row) is greater than the puzzle number of rows({cls.rows})")
        
        if len(col_vals) != cls.cols:
            raise SelectError((f"Number of columns({len(col_vals)} != puzzle number of columns({cls.cols})"))
        
        for ic, col_val in enumerate(col_vals):
            cls.sudoku_puzzle.add_cell(row=cls.cur_row, col=ic+1, val=col_val)
        if SlTrace.trace("puzzle_load"):
            cls.sudoku_puzzle.display(f"row={cls.cur_row}")
        
    @classmethod
    def end_puzzle(cls):
        pass
    
if __name__ == "__main__":
    from tkinter import filedialog
    
    start_dir = r"./puzzle"
    filename =  filedialog.askopenfile(
        initialdir = start_dir,
        title = "Select puzzle file",
        filetypes = (("supz files","*.supz"),("all files","*.*")))
    
    spl = SudokuPuzzleLoad.set_input(pfile=filename)
    puzzle1 = spl.procCmdString()
    puzzle1.display('puzzle1 display')
    
    puzzle2 = spl.get_puzzle()
    puzzle2.display("get_puzzle display")        
    

    puzzle3 = SudokuPuzzleLoad.file2puzzle(file=filename)
    puzzle3.display("get_puzzle display")        

