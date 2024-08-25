# vim: set ts=2 sw=2 sts=2 et:
from lib import *
from col import COL

@dataclass
class SYM(COL):
  """SYMs tracks  symbol counts  and tracks the `mode` 
  (the most common frequent symbol)."""
  has  : dict = DICT()
  mode : atom=None
  most : int=0

  def add1(self, x:any) -> any:
    "add symbol counts."
    self.has[x] = self.has.get(x,0) + 1
    if self.has[x] > self.most: self.mode, self.most = x, self.has[x]
    return x

  def clone(self): 
    "Copy structure of self."
    return SYM(at=self.at,txt=self.txt)

  def div(self) -> number: 
    "Return diversity of a SYM."
    return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

  def dist1(self, x:number, y:number) -> float: 
    "Distance between two SYMs."
    return x != y

  def exploit(self, other:Self):
    "Guess a value that is more like `self` than  `other`."
    priora = self.n/(self.n + other.n)
    priorb = other.n/(self.n + other.n)
    a = self.like(self.mid(),  priora)
    b = other.like(self.mid(), priorb)
    c = a - b
    return c,self,self.mid(),

  def like(self, x:any, prior:float) -> float:
    "How much a SYM likes a value `x`."
    return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

  def mid(self) -> number: 
    "Return central tendency of SYMs."
    return self.mode

  def predict(self, pairs:list[tuple[float,any]]) -> number:
    "Sort symbols by votes (voting by distance)."
    votes = {}
    for d,x in pairs:
      votes[x] = votes.get(x,0) + 1/d**2
    return max(votes, key=votes.get)
