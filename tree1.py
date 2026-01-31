#!/usr/bin/env python3 -B
"""
ez.py: easy AI tools
(c) 2025 Tim Menzies, MIT license

Options:
   -b bins=5    Number of bins
   -B Budget=50 Initial sampling budget 
   -C Check=5   final evaluation budget
   -l leaf=2    Min examples in leaf of tree
   -p p=2       Distance coefficient
   -s seed=1    Random number seed
   -S Show=30   Tree display width"""
from functools import reduce
from math import log,exp,sqrt
import re,sys,random,traceback
BIG=1e32

#-------------------------------------------------------------------------------
# Create
def NUM(**d): return OBJ(it=NUM, **d, n=0, mu=0, m2=0)
def SYM(**d): return OBJ(it=SYM, **d, n=0, has={})
def COL(at=0,txt=" "):
  return (NUM if txt[0].isupper() else SYM)(at=at, txt=txt, goal=txt[-1]!="-")

def DATA(items=[], s=""):
  return adds(items, OBJ(it=DATA, txt=s, rows=[], cols=None))

def COLS(names):
  cols = [COL(at=n,txt=s) for n,s in enumerate(names)]
  return OBJ(it=COLS, names=names, all=cols,
             x=[c for c in cols if c.txt[-1] not in "-+!X"],
             y=[c for c in cols if c.txt[-1]     in "-+!"])

def clone(data, rows=[]): return DATA(items=[data.cols.names] + rows)

#-------------------------------------------------------------------------------
# Update
def adds(items, it=None):
  it = it or NUM(); [add(it,item) for item in items]; return it

def add(i,v):
  if DATA is i.it: 
    if not i.cols: i.cols = COLS(v)
    else: i.rows += [[add(c,v[c.at]) for c in i.cols.all]]
  elif v != "?":
    i.n += 1
    if SYM is i.it: i.has[v] = 1 + i.has.get(v,0)
    if NUM is i.it: d = v - i.mu; i.mu += d/i.n; i.m2 += d*(v - i.mu)
  return v

def merge(a, b):
  c = NUM()
  c.n = a.n + b.n
  if c.n:
    c.mu = (a.n*a.mu + b.n*b.mu) / c.n
    c.m2 = a.m2 + b.m2 + (a.mu - b.mu)**2 * a.n * b.n / c.n
  return c

def merges(bins): return reduce(lambda a,b: merge(a,b[1]), bins, NUM())

#-------------------------------------------------------------------------------
# Query
def score(n, mu, sd): return mu + sd/(sqrt(n) + 1/BIG)

def mids(data):  return [mid(col) for col in data.cols.all]
def mid(col):    return mode(col) if SYM is col.it else col.mu
def mode(sym):   return max(sym.has, key=sym.has.get)

def spread(col): return (ent if SYM is col.it else sd)(col)
def sd(num):     return 0 if num.n < 2 else sqrt(num.m2 / (num.n - 1))
def ent(sym):
  return -sum(p*log(p,2) for n in sym.has.values() if (p := n/sym.n) > 0)

def z(num,v):    return (v - num.mu) / (sd(num) + 1/BIG)
def norm(num,x): return 1 / (1 + exp(-1.7 * x))
def bucket(col,v):
  if v=="?" or SYM is col.it: return v
  return int(the.bins * norm(col, clip(z(col,v), -3, 3)))

#-------------------------------------------------------------------------------
# Distance
def minkowski(items):
  n, d = 0, 0
  for item in items: n, d = n+1, d + item**the.p
  return 0 if n==0 else (d/n) ** (1/the.p)

def disty(data, row):
  return minkowski(abs(norm(y,z(y,row[y.at])) - y.goal) for y in data.cols.y)

def distx(data, r1, r2):
  return minkowski(aha(x, r1[x.at], r2[x.at]) for x in data.cols.x)

def aha(col, u, v):
  if u == v == "?": return 1
  if SYM is col.it: return u != v
  u, v = norm(col,z(col,u)), norm(col,z(col,v))
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

def around(data, row, rows): return sorted(rows, key=lambda r: distx(data,row,r))

#-------------------------------------------------------------------------------
# Tree
def cuts(d, cols):
  for col in cols:
    bins = [(b,num) for (at,b),num in d.items() if at == col.at]
    if not bins: continue
    if SYM is col.it:
      for b,num in bins: yield (score(num.n, num.mu, sd(num)), col.at, b)
    else:
      bins.sort()
      for j in range(len(bins)-1):
        lhs, rhs = merges(bins[:j+1]), merges(bins[j+1:])
        n = lhs.n + rhs.n
        mu = (lhs.n*lhs.mu + rhs.n*rhs.mu) / n
        s = (lhs.n*sd(lhs) + rhs.n*sd(rhs)) / n
        yield (score(n, mu, s), col.at, bins[j][0])

def bestcut(data, rows):
  d = {}
  for r in rows:
    y = disty(data, r)
    for col in data.cols.x:
      k = (col.at, bucket(col, r[col.at]))
      if k[1] != "?":
        if k not in d: d[k] = NUM()
        add(d[k], y)
  return min(cuts(d, data.cols.x), default=(BIG,None,None))[1:]

def Tree(data, uses=None):
  uses = uses or set()
  def grow(rows):
    at, b, kids = None, None, {}
    if len(rows) > the.leaf*2:
      at, b = bestcut(data, rows)
      if at is not None:
        col = data.cols.all[at]
        ok, no = [], []
        for r in rows: (ok if b == bucket(col,r[at]) else no).append(r)
        if ok and no:
          uses.add(at)
          kids = {True: grow(ok), False: grow(no)}
        else: at, b = None, None
    return OBJ(root=data, kids=kids, at=at, bucket=b,
               x=mids(clone(data,rows)), y=adds(disty(data,r) for r in rows))
  return grow(data.rows), uses

def treeLeaf(t, row):
  if not t.kids: return t
  col = t.root.cols.all[t.at]
  return treeLeaf(t.kids[bucket(col, row[col.at]) == t.bucket], row)

def treeShow(t):
  def show(n, lvl, pre):
    g = [n.x[c.at] for c in n.root.cols.y]
    print(f"{('| '*(lvl-1)+pre):{the.Show}}: {o(n.y.mu):6} : {n.y.n:4} : {o(g)}")
    for k in sorted(n.kids or {}, reverse=True):
      c, b = n.root.cols.all[n.at], n.bucket
      s = f"{c.txt} {'==' if k else '!='} {b}" if SYM is c.it else \
          f"{c.txt} {'<=' if k else '>'} bin{b}"
      show(n.kids[k], lvl+1, s)
  ys = ', '.join([y.txt for y in t.root.cols.y])
  print(f"{'':{the.Show}}   Score      N   [{ys}]"); show(t, 0, "")

#-------------------------------------------------------------------------------
# Lib
def clip(v, lo, hi): return max(lo, min(hi, v))
def shuffle(lst): random.shuffle(lst); return lst

def o(t):
  match t:
    case dict(): return "{" + " ".join(f":{k} {o(t[k])}" for k in t) + "}"
    case float(): return f"{int(t)}" if int(t) == t else f"{t:.2f}"
    case list(): return "[" + ", ".join(o(x) for x in t) + "]"
    case _: return str(t)

class OBJ(dict):
  __getattr__, __setattr__, __repr__ = dict.__getitem__, dict.__setitem__, o

def gauss(mu, sd1):
  return mu + 2*sd1*(sum(random.random() for _ in range(3)) - 1.5)

def cast(s, BOOL={"true": True, "false": False}):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return BOOL.get(s, s)

def csv(f):
  with open(f) as file:
    for s in file: yield [cast(x) for x in s.split(",")]

#-------------------------------------------------------------------------------
# CLI
def eg_h():
  "Show help."
  print(__doc__)
  for k,v in globals().items():
    if k.startswith("eg_"): print(f"   -{k[3:]:<12}{v.__doc__}")

def eg__the(): "Show config."; print(the)

def eg_s(n:int): "Set seed."; the.seed = n; random.seed(n)

def eg__csvs(f:str): "CSV reader."; [print(row) for row in list(csv(f))[::40]]

def eg__syms():
  "SYM test."
  syms = adds("aaaabbc", SYM()); print(o(x := ent(syms)))
  assert abs(1.379 - x) < .05

def eg__nums():
  "NUM test."
  nums = adds(gauss(10,1) for _ in range(1000))
  print(OBJ(mu=nums.mu, sd=sd(nums)))
  assert abs(10 - nums.mu) < .05 and abs(1 - sd(nums)) < .05

def eg__ys(f:str):
  "Show y values."
  data = DATA(csv(f))
  for row in sorted(data.rows, key=lambda r: disty(data,r))[::40]:
    print(*row, round(disty(data,row),2))

def eg__tree(f:str):
  "Build tree."
  data = DATA(csv(f))
  tree, _ = Tree(clone(data, shuffle(data.rows)[:50]))
  treeShow(tree)

def eg__test(f:str):
  "Test tree."
  data = DATA(csv(f))
  mid = len(data.rows)//2
  Y = lambda r: disty(data, r)
  b4 = sorted(Y(r) for r in data.rows)
  win = lambda r: int(100*(1 - (Y(r) - b4[0]) / (b4[mid] - b4[0] + 1/BIG)))
  wins = NUM()
  for _ in range(20):
    rows = shuffle(data.rows)
    test, train = rows[mid:], rows[:mid][:the.Budget]
    tree, _ = Tree(clone(data, train))
    test.sort(key=lambda r: treeLeaf(tree,r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[mid])} ,lo {o(b4[0])}",
        *[f"{s} {len(a)}" for s,a in 
          dict(x=data.cols.x, y=data.cols.y, r=data.rows).items()],
        *f.split("/")[-2:], sep=" ,")

#-------------------------------------------------------------------------------
the = OBJ(**{k: cast(v) for k,v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

if __name__ == "__main__":
  args = iter(sys.argv[1:])
  for s in args:
    if f := globals().get(f"eg_{s[1:].replace('-','_')}"):
      random.seed(the.seed)
      try: f(*[t(next(args)) for t in f.__annotations__.values()])
      except Exception: traceback.print_exc()
    elif s[1:] in the: the[s[1:]] = cast(next(args, ""))
