# vim: set ts=2 sw=2 sts=2 et:
from lib import *
from col import COL

@dataclass
class NUM(COL):
  """NUMs tracks  `lo,hi` seen so far, as well the `mu` (mean) and `sd` 
  (standard deviation), using Welford's algorithm. """
  mu : number =  0
  m2 : number =  0
  sd : number =  0
  lo : number =  1E32
  hi : number = -1E32
  goal : number = 1

  def __post_init__(self) -> None:
    """A minus sign at end of a NUM's name says "this is a 
    column to minimize" (all other goals are to be maximizes)."""
    if  self.txt and self.txt[-1] == "-": self.goal=0

  def add1(self, x:any) -> number:
    "add `mu` and `sd` (and `lo` and `hi`). If `x` is a string, coerce to a number."
    self.lo  = min(x, self.lo)
    self.hi  = max(x, self.hi)
    d        = x - self.mu
    self.mu += d / self.n
    self.m2 += d * (x -  self.mu)
    self.sd  = 0 if self.n <2 else (self.m2/(self.n-1))**.5

  def clone(self): 
    "Mimic structure of self"
    return NUM(at=self.at,txt=self.txt)

  def dist1(self, x:number, y:number) -> float:
    "Distance between two NUMs."
    x, y = self.norm(x), self.norm(y)
    x = x if x !="?" else (1 if y<0.5 else 0)
    y = y if y !="?" else (1 if x<0.5 else 0)
    return abs(x-y)

  def div(self) -> number: 
    "Return diversity of a NUM."
    return self.sd

  def exploit(self, other:Self):
    "Guess a value that is more like `self` than  `other`."
    a = self.like(self.mid())
    b = other.like(self.mid())
    c = (self.n*a - other.n*b)/(self.n + other.n)
    return c,self,self.mid()

  def like(self, x:number, prior=None) -> float:
    "How much a NUM likes a value `x`."
    v     = self.sd**2 + 1E-30
    nom   = exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
    denom = (2*pi*v) **0.5
    return max(0,min(1, nom/(denom + 1E-30)))

  def mid(self) -> number: 
    "Return central tendency of NUMs."
    return self.mu

  def norm(self, x) -> number:
    "Returns 0..1 for min..max."
    return x if x=="?" else  ((x - self.lo) / (self.hi - self.lo + 1E-32))

  def predict(self, pairs:list[tuple[float,number]]) -> number:
    "Find weighted sum of numbers (weighted by distance)."
    ws,tmp = 0,0
    for d,num in pairs:
      w    = 1/d**2
      ws  += w
      tmp += w*num
    return tmp/ws

