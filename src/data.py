# vim: set ts=2 sw=2 sts=2 et:
from lib import *
from cols import COLS

@dataclass
class DATA:
  cols : COLS = None         # summaries of rows
  rows : rows = LIST() # rows

  def activeLearning(self, score=lambda B,R: B-R, generate=None, faster=True ):
    "active learning"
    def ranked(rows): return self.clone(rows).chebyshevs().rows
  
    def todos(todo):
      if faster: # Apply our sorting heuristics to just a small buffer at start of "todo"
        # rotate back half of buffer to end of list, fill the gap with later items
         n = the.buffer//2
         return todo[:n] + todo[2*n: 3*n],  todo[3*n:] + todo[n:2*n]
      else: # Apply our sorting heuristics to all of todo.
        return todo,[]
  
    def guess(todo:rows, done:rows) -> rows:
      cut  = int(.5 + len(done) ** the.cut)
      best = self.clone(done[:cut])
      rest = self.clone(done[cut:])
      a,b  = todos(todo)
      the.iter = len(done) - the.label
      if generate:
        return self.neighbors(generate(best,rest), a) + b
      else:
        key  = lambda r: score(best.loglike(r, len(done), 2), rest.loglike(r, len(done), 2))
        return  sorted(a, key=key, reverse=True) + b
  
    def loop(todo:rows, done:rows) -> rows:
      while len(todo) > 2 and len(done) < the.Last:
        top,*todo = guess(todo, done)
        done     += [top]
        done      = ranked(done)
      return done
  
    todo, done = self.rows[the.label:], ranked(self.rows[:the.label])
    if the.branch == True:
      todo, done = self.branch(used = [])
    return loop(todo, done)

  def add(self,row:row) -> Self:
    """As a side-effect on adding one row (to `rows`), update
    the column summaries (in `cols`)."""
    if    self.cols: self.rows += [self.cols.add(row)]
    else: self.cols = COLS(names=row) # for row q
    return self

  # XXX:not sure on return types being two different types.
  def branch(self, region:rows=None, stop=None, used=[], evals=1):
    "Recursively bi-cluster `region`, recurse only down the best half."
    region = region or self.rows
    if not stop: random.shuffle(region)
    stop = stop or the.Stop
    if len(region) > stop:
      distance, lefts, rights, left, right = self.half(region, True)
      if left not in used:
          used.append(left)
      if right not in used:
           used.append(right)
      return self.branch(lefts, stop, used, evals + 1)
    else:
      return [r for r in self.rows if r not in used], used

  def chebyshev(self,row:row) -> number:
    "Compute Chebyshev distance of one row to the best `y` values."
    return  max(abs(col.goal - col.norm(row[col.at])) for col in self.cols.y)
  
  def chebyshevs(self) -> Self:
    "Sort rows by Chebyshev distance."
    self.rows = sorted(self.rows, key=lambda r: self.chebyshev(r))
    return self

  def clone(self, rows:rows=[]) -> Self:
    """Another way to create a DATA is to copy the columns structure of
    an existing DATA, then maybe load in some rows to that new DATA."""
    return DATA().add(self.cols.names).adds(rows)

  def cluster(self, rows:rows=None,  sortp=False, stop=None, cut=None, fun=None, lvl=0):
    "recursive divide rows using distance to two far points"
    stop = stop or the.Stop
    rows = rows or self.rows
    cut1, ls, rs, left, right = self.half(rows,sortp=sortp)
    it = CLUSTER(data=self.clone(rows), cut=cut, fun=fun, 
                 left=left, right=right, mid=rs[0], lvl=lvl)
    if len(ls)>stop and len(ls)<len(rows): 
      it.lefts  = self.cluster(ls, sortp, stop, cut1, le, lvl+1)
    if len(rs)>stop and len(rs)<len(rows): 
      it.rights = self.cluster(rs, sortp, stop, cut1, gt, lvl+1)
    return it

  def d2h(self,row:row) -> number:
    "Compute euclidean distance of one row to the best `y` values."
    d = sum(abs(c.goal - c.norm(row[c.at]))**2 for c in self.cols.y)
    return (d/len(self.cols.y)) ** (1/the.p)

  def d2hs(self) -> Self:
    "Sort rows by the Euclidean distance of the goals to heaven."
    self.rows = sorted(self.rows, key=lambda r: self.d2h(r))
    return self

  def dist(self, r1:row, r2:row) -> float:
    "Euclidean distance between two rows."
    n = sum(c.dist(r1[c.at], r2[c.at])**the.p for c in self.cols.x)
    return (n / len(self.cols.x))**(1/the.p)

  def diversity(self, rows:rows=None, stop=None):
    "Diversity sampling (one per items)."
    rows = rows or self.rows
    cluster = self.cluster(rows, stop=stop or math.floor(len(rows)**0.5))
    for node,leafp in cluster.nodes():
      if leafp:
          yield node.mid
  
  def exploit(self, other:Self, top=1000, used=None):
    "Guess a row more like `self` than `other`."
    out = ["?" for _ in self.cols.all]
    for _,col,x in sorted([coli.exploit(colj) 
                           for coli,colj in zip(self.cols.x, other.cols.x)],
                           reverse=True,key=nth(0))[:top]:
       out[col.at] = x
       # if used non-nil, keep stats on what is used
       if used != None:
          used[col.at] = used.get(col.at,None) or col.clone()
          used[col.at].add(x)
    return out

  def half(self, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
    "Divide rows by distance to two faraway points"
    return self.half_median(rows,True) if the.median else self.half_mean(rows,True)
  
  def half_mean(self, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
    "Divide rows by distance to two faraway points"
    left,right = self.twoFar(rows, sortp=sortp)
    C = self.dist(left,right)
    lefts,rights = [],[]
    project = lambda row: (self.dist(row,left)**2 + C**2 - self.dist(row,right)**2)/(2*C + 1E-30)
    for row in rows:
      (lefts if project(row) <= C/2 else rights).append(row)
    return self.dist(left,lefts[-1]),lefts, rights, left, right
  
  def half_median(self, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
    "Divide rows by distance to two faraway points"
    mid = int(len(rows) // 2)
    left,right = self.twoFar(rows, sortp=sortp)
    C = self.dist(left,right)
    project = lambda row: (self.dist(row,left)**2 + C**2 - self.dist(row,right)**2)/(2*C + 1E-30)
    tmp = sorted(self.rows, key=project)
    return self.dist(left,tmp[mid]), tmp[:mid], tmp[mid:], left, right

  def loglike(self, r:row, nall:int, nh:int) -> float:
    "How much DATA likes a `row`."
    prior = (len(self.rows) + the.k) / (nall + the.k*nh)
    likes = [c.like(r[c.at], prior) for c in self.cols.x if r[c.at] != "?"]
    return sum(log(x) for x in likes + [prior] if x>0)

  def mid(self) -> row:
    "Return central tendency of a DATA."
    return [col.mid() for col in self.cols.all]
 
  def neighbors(self, row1:row, rows:rows=None) -> rows:
    "Sort `rows` by their distance to `row1`'s x values."
    return sorted(rows or self.rows, key=lambda row2: self.dist(row1, row2))  

  def predict(self, row1:row, rows:rows, cols=None, k=2):
    "Return predictions for `cols` (defaults to klass column)."
    cols = cols or self.cols.y
    got = {col.at : [] for col in cols}
    for row2 in self.neighbors(row1, rows)[:k]:
      d =  1E-32 + self.dist(row1,row2)
      [got[col.at].append( (d, row2[col.at]) )  for col in cols]
    return {col.at : col.predict( got[col.at] ) for col in cols}
   
  def shuffle(self) -> Self:
    "Sort rows randomly"
    random.shuffle(self.rows)
    return self

  def twoFar(self, rows:rows, sortp=False, samples:int=None) -> tuple[row,row] :
    "Return two distant rows, optionally sorted into best, then rest"
    left, right =  max(((one(rows), one(rows)) for _ in range(samples or the.fars)),
                         key= lambda two: self.dist(*two))
    if sortp and self.chebyshev(right) < self.chebyshev(left): right,left = left,right
    return left, right

@dataclass
class CLUSTER:
  data   : DATA
  right  : row
  left   : row
  mid    : row
  cut    : number
  fun    : Callable
  lvl    : int = 0
  lefts  : Self = None
  rights : Self = None

  def __repr__(self) -> str:
    return f"{'|.. ' * self.lvl}{len(self.data.rows)}"

  def leaf(self, data:DATA, row:row) -> Self:
    d = data.dist(self.left,row)
    if self.lefts  and self.lefts.fun( d,self.lefts.cut):  return self.lefts.leaf(data,row)
    if self.rights and self.rights.fun(d,self.rights.cut): return self.rights.leaf(data,row)
    return self

  def nodes(self):
    def leafp(x): return x.lefts==None or x.rights==None
    yield self, leafp(self)
    for node in [self.lefts,self.rights]:
      if node:
        for x,isLeaf in node.nodes(): yield x, isLeaf
