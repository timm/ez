# vim: set ts=2 sw=2 sts=2 et:
from lib import *

@dataclass
class COL:
  """NUMs and SYMs are both COLumns. All COLumns count `n` (items seen),
  `at` (their column number) and `txt` (column name)."""
  n   : int = 0
  at  : int = 0
  txt : str = ""

  def add(self, x:any) -> any:
    "If `x` is known, add this COL."
    if x != "?":
      self.n += 1
      self.add1(x)

  def dist(self, x:any, y:any) -> float:
    "Between two values (Aha's algorithm)."
    return 1 if x==y=="?" else self.dist1(x,y)
