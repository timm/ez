#!/usr/bin/env python3 -B
"""
ez.py: easy AI tools
(c) 2025 Tim Menzies, MIT license

Options:
   -b bins=7    Number of bins
   -l leaf=4    Min examples in leaf of tree
   -p p=2       Distance coeffecient
   -s seed=1    Random number seed
   -w width=30  Tree display width 
"""
from math import log,exp,sqrt
import re,sys,random,traceback
BIG=1e32

#-------------------------------------------------------------------------------
# Create
def COL(at=0,txt=" "): return obj(txt=txt, at=at, n=0, goal=txt[-1]!="-")
def NUM(**d):          return obj(it=NUM, **COL(**d), mu=0, m2=0, lo={})
def SYM(**d):          return obj(it=SYM, **COL(**d), has={})
def DATA(items):
  items = iter(items)
  return adds(items, obj(it=DATA, n=0, rows=[], cols=COLS(next(items))))

def COLS(names):
  cols= [(NUM if s[0].isupper() else SYM)(at=n,txt=s) for n,s in enumerate(names)]
  return obj(it=COLS, names=names, all=cols,
            x= [c for c in cols if c.txt[-1] not in "-+X"],
            y= [c for c in cols if c.txt[-1]     in "-+" ])

def clone(data, rows=None): return DATA([data.cols.names] + (rows or []))

#-------------------------------------------------------------------------------
# Update
def adds(items, it=None):
  it = it or NUM(); [add(it,item) for item in items]; return it

def add(i,v):
  if v != "?":
    i.n += 1
    if   DATA is i.it : i.rows += [[add(c,v[c.at]) for c in i.cols.all]]
    elif  SYM is i.it : i.has[v] = 1 + i.has.get(v,0)
    elif  NUM is i.it : d = v - i.mu; i.mu += d/i.n; i.m2 += d*(v - i.mu)
    else: raise TypeError(f"add error on '{type(i)}'")
  return v

#-------------------------------------------------------------------------------
# Query
def mids(data):  return [mid(col) for col in data.cols.all]
def mid(col):    return mode(col) if SYM is col.it else col.mu
def mode(sym):   return max(sym.has, key=sym.has.get)

def spread(col): return (ent if SYM is col.it else sd)(col)
def sd(num):     return 0 if num.n < 2 else sqrt(num.m2 / (num.n - 1))
def ent(sym):    return -sum(p*log(p,2) for n in sym.has.values() if (p:=n/sym.n)>0)

def z(num,v):    return (v -  num.mu) / (sd(num) + 1/BIG)
def norm(num,v): return 1 / (1 + exp( -1.7 * max(-3, min(3, z(num,v)))))
def bucket(col,v):
  if v=="?" or  SYM is col.it: return v
  b = int(the.bins * norm(col,v))
  col.lo[b] = min(v, col.lo.get(b,v))
  return b

def score(num):
  return BIG if num.n < the.leaf else num.mu + sd(num) /(sqrt(num.n) + 1/BIG)

def b2v(num,b): # inverse discretization
  if b==0: return -BIG. num.lo[b]
  if b==the.bins-1: return num.lo[b], BIG
  return num.lo[b], num.lo[b+1]

def minkowski(items):
  n,d = 0,0
  for item in items: n, d = n+1, d+item ** the.p
  return 0 if n==0 else (d / n) ** (1 / the.p)

def disty(data, row):
  return minkowski(((norm(y,row[y.at]) - y.goal) for y in data.cols.y))

def distx(data,row1,row2):
  return minkowski(aha(x, row1[x.at], row2[x.at]) for x in data.cols.x)

def aha(col,u,v):
  if u==v=="?": return 1
  if SYM is col.it : return u != v
  u,v = norm(col,u), norm(col,v)
  u = u if u != "?" else (0 if v>0.5 else 1)
  v = v if v != "?" else (0 if u>0.5 else 1)
  return abs(u - v)

def nearest(data, row, rows=None):  
  return min(rows or data.rows, key=lambda r: distx(data, row, r))

#-------------------------------------------------------------------------------
# tree
def Tree(data, uses=None):
  uses = uses or set()
  def bestcut(rows):
    d={}
    for r in rows:
      y = disty(data,r)
      for col in data.cols.x:
        k = (col.at, bucket(col, r[col.at]))
        if k not in d: d[k] = NUM()
        add(d[k], y)
    return min(d.items(), key=lambda x: score(x[1]), default=None)

  def grow(rows):
    at, b, kids = None, None, {}
    if len(rows) > the.leaf*2:
      if cut := bestcut(rows):
        ((at,b), _) = cut
        ok, no = [], []
        for r in rows:
          (ok if b == bucket(data.cols.all[at], r[at]) else no).append(r)
        if ok and no:
          uses.add(at)
          kids = {True:grow(ok), False:grow(no)}
    return obj(root=data, kids=kids, at=at, bucket=b,
               x= mids(clone(data,rows)),
               y= adds(disty(data,row) for row in rows))

  return grow(data.rows), uses

def treeShow1(t, lvl, cut):
  w, g = the.width, [t.x[c.at] for c in t.root.cols.y]
  print(f"{('| '*(lvl-1)+cut):{w}}: {o(t.y.mu):6} : {t.y.n:4} : {o(g)}")
  [treeShow1(t.kids[k], lvl+1, 
             f"{t.root.cols.names[t.at]} {'==' if k else '!='} {t.bucket}") 
   for k in sorted(t.kids or {}, reverse=True)]

def treeShow(t):
  w = the.width
  print(f"{'':{w}}  Score    N     {[c.txt for c in t.root.cols.y]}")
  print(f"{'':{w}}  -----  ----    ---------")
  treeShow1(t, 0, ".")
  print(f"\n{'':{w}}  Discrete Ranges (b2v):")
  for c in t.root.cols.x:
    try: print(f"{c.txt:{w}}: {[o(b2v(c,b)) for b in range(the.bins)]}") 
    except: pass
  print(f"{'bins':{w}}: {[b for b in range(1,the.bins+1)]}")

#------------------------------------------------------------------------------
# lib
def o(v):
  if isinstance(v, float): return round(v, 2)
  if isinstance(v, (list, tuple, set)): return [o(x) for x in v]
  if isinstance(v, dict):
    return "[" + " ".join([f":{k} {o(val)}" for k, val in v.items()]) + "]"
  if hasattr(v, '__name__'): return v.__name__
  if hasattr(v, '__dict__'): return f"{type(v).__name__}{o(vars(v))}"
  return v

class obj(dict):
  __getattr__, __setattr__, __repr__ = dict.__getitem__, dict.__setitem__, o

def gauss(mu,sd):
  return mu + 2 * sd * (sum(random.random() for _ in range(3)) - 1.5)

def pick(d,n):
  n *= random.random()
  for k,v in d.items(): 
    if (n := n-v) <= 0: break
  return k

def era(items, size=20):
  cache = []
  for item in items:
    cache += [item]
    if len(cache) > size: yield shuffle(cache); cache=[]
  if cache: yield shuffle(cache)

def shuffle(lst): random.shuffle(lst); return lst

def cast(s, FUN=(int, float), BOOL={"true": True, "false": False}):
  for fn in FUN:
    try: return fn(s)
    except ValueError: pass
  return BOOL.get(s, s)

def csv(fileName):
  with open(fileName, encoding="utf-8") as f:
    for l in f:
      l = re.sub(r'\s+', '', l.split("#")[0]) # no whitespace, skip comments
      if l:
        yield [cast(x) for x in l.split(",")]

#-------------------------------------------------------------------------------
# cli
def config(s=__doc__):
  return obj(**{m[0]:cast(m[1]) for m in re.findall(r"(\w+)=(\S+)", s)})

def cli(funs,d,flags):
  for n, s in enumerate(flags):
    v = cast(flags[n + 1]) if n < len(flags) - 1 else None
    if f := funs.get(f"go{s.replace('-', '_')}"): 
      try: f(v)
      except Exception: traceback.print_exc()
    elif (k := s.lstrip("-")[0]) in d: d[k] = v

def go_h(_)    : print(__doc__)
def go__the(_) : print(the)
def go_s(n)    : the.seed=n; random.seed(n)
def go__csv(f) : [print(row) for row in list(csv(f))[::40]]

def go__syms(_):
    syms = adds("aaaabbc",SYM()); print(o(x:=ent(syms))); assert abs(1.379-x) < .05

def go__nums(_):
  nums = adds(gauss(10, 1) for _ in range(1000))
  print(obj(mu=nums.mu, sd=sd(nums)))
  assert abs(10 - nums.mu) < .05 and abs(1 - sd(nums)) < .05

def go__ys(f):
  data = DATA(csv(f))
  print(*data.cols.names)
  print(o(mids(data)))
  for row in sorted(data.rows, key=lambda r: disty(data, r))[::40]:
    print(*row,*[bucket(col,row[col.at]) for col in data.cols.y], 
          round(disty(data,row),2))

def go__tree(f):
  data = DATA(csv(f))
  data1 = clone(data, shuffle(data.rows)[:50])
  tree,_ = Tree(data1)
  treeShow(tree)

#------------------------------------------------------------------------------
the = config()
random.seed(the.seed)
if __name__=="__main__": cli(vars(),the,sys.argv)
