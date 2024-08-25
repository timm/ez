# vim: set ts=2 sw=2 sts=2 et:
from lib import *
import COL

@dataclass
class SYM(COL.COL):
  """SYMs tracks  symbol counts  and tracks the `mode` 
  (the most common frequent symbol)."""
  has  : dict = DICT()
  mode : atom=None
  most : int=0

  def add1(self:SYM, x:any) -> any:
    "add symbol counts."
    self.has[x] = self.has.get(x,0) + 1
    if self.has[x] > self.most: self.mode, self.most = x, self.has[x]
    return x

  def clone(self:SYM): 
    "Copy structure of self."
    return SYM(at=self.at,txt=self.txt)

  def div(self:SYM) -> number: 
    "Return diversity of a SYM."
    return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

  def dist1(self:SYM, x:number, y:number) -> float: 
    "Distance between two SYMs."
    return x != y

  def exploit(self:SYM, other:SYM):
    "Guess a value that is more like `self` than  `other`."
    priora = self.n/(self.n + other.n)
    priorb = other.n/(self.n + other.n)
    a = self.like(self.mid(),  priora)
    b = other.like(self.mid(), priorb)
    c = a - b
    return c,self,self.mid(),

  def like(self:SYM, x:any, prior:float) -> float:
    "How much a SYM likes a value `x`."
    return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

  def mid(self:SYM) -> number: 
    "Return central tendency of SYMs."
    return self.mode

  def predict(self:SYM, pairs:list[tuple[float,any]]) -> number:
   "Sort symbols by votes (voting by distance)."
    votes = {}
    for d,x in pairs:
      votes[x] = votes.get(x,0) + 1/d**2
    return max(votes, key=votes.get)
