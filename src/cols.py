from lib import *
from col import COL
from num import NUM
from sym import SYM

@dataclass
class COLS:
  """COLS are a factory that reads some `names` from the first
  row , the creates the appropriate columns."""
  names: list[str]   # column names
  all  : list[COL] = LIST()  # all NUMS and SYMS
  x    : list[COL] = LIST()  # independent COLums
  y    : list[COL] = LIST()  # dependent COLumns
  klass: COL = None

  def __post_init__(self) -> None:
    """Collect  `all` the COLs as well as the dependent/independent 
    `x`,`y` lists. Upper case names are NUMerics. Anything ending in 
    `+` or `-` is a goal to  be maximized of minimized. Anything 
    ending in `X` is ignored."""
    for at,txt in enumerate(self.names):
      a,z = txt[0],txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at, txt=txt)
      self.all.append(col)
      if z != "X":
        (self.y if z in "!+-" else self.x).append(col)
        if z=="!": self.klass = col
        if z=="-": col.goal = 0

def add(self, row:row) -> row:
  "add all the `x` and `y` cols."
  [col.add(row[col.at]) for cols in [self.x, self.y] for col in cols]
  return row
