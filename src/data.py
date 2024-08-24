from types import *

# NUMs and SYMs are both COLumns. All COLumns count `n` (items seen),
# `at` (their column number) and `txt` (column name).
@dataclass
class COL:
  n   : int = 0
  at  : int = 0
  txt : str = ""

# SYMs tracks  symbol counts  and tracks the `mode` (the most common frequent symbol).
@dataclass
class SYM(COL):
  has  : dict = DICT()
  mode : atom=None
  most : int=0

  def clone(self:SYM): return SYM(at=self.at,txt=self.txt)

# NUMs tracks  `lo,hi` seen so far, as well the `mu` (mean) and `sd` (standard deviation),
# using Welford's algorithm.
@dataclass
class NUM(COL):
  mu : number =  0
  m2 : number =  0
  sd : number =  0
  lo : number =  1E32
  hi : number = -1E32
  goal : number = 1

 def clone(self:NUM): return NUM(at=self.at,txt=self.txt)

  # A minus sign at end of a NUM's name says "this is a column to minimize"
  # (all other goals are to be maximizes).
  def __post_init__(self:NUM) -> None:
    if  self.txt and self.txt[-1] == "-": self.goal=0

# COLS are a factory that reads some `names` from the first
# row , the creates the appropriate columns.
@dataclass
class COLS:
  names: list[str]   # column names
  all  : list[COL] = LIST()  # all NUMS and SYMS
  x    : list[COL] = LIST()  # independent COLums
  y    : list[COL] = LIST()  # dependent COLumns
  klass: COL = None

  # Collect  `all` the COLs as well as the dependent/independent `x`,`y` lists.
  # Upper case names are NUMerics. Anything ending in `+` or `-` is a goal to
  # be maximized of minimized. Anything ending in `X` is ignored.
  def __post_init__(self:COLS) -> None:
    for at,txt in enumerate(self.names):
      a,z = txt[0],txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at, txt=txt)
      self.all.append(col)
      if z != "X":
        (self.y if z in "!+-" else self.x).append(col)
        if z=="!": self.klass = col
        if z=="-": col.goal = 0

# DATAs store `rows`, which are summarized in `cols`.
@dataclass
class DATA:
  cols : COLS = None         # summaries of rows
  rows : rows = LIST() # rows

  # Another way to create a DATA is to copy the columns structure of
  # an existing DATA, then maybe load in some rows to that new DATA.
  def clone(self:DATA, rows:rows=[]) -> DATA:
    return DATA().add(self.cols.names).adds(rows)
