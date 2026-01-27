#!/usr/bin/env python3 -B
"""
tree.py: tree learning for ezr.py
(c)2026 Tim Menzies, MIT license.

Options:
   -b bins=16   Number of bins
   -B Budget=50 Initial sampling budget 
   -C Check=5   Final evaluation budget
   -l leaf=2    Min examples in leaf of tree
   -s seed=1    Random number seed
   -S Show=30   Tree display width 
"""
import re, sys, random, traceback
from ezr import *

BIG = 1E32
the = Obj(**{k: cast(v) for k, v in re.findall(r"(\w+)=(\S+)", __doc__)})
random.seed(the.seed)

# --- tree helpers ---------------------------------------------------
def bin(col, x):
  if x == "?" or "has" in col: return x
  tmp = (col.hi - col.lo) / (the.bins - 1)
  return 1 if col.hi == col.lo else int(x / tmp + 0.5) * tmp

def sub(i, v):
  if v != "?" and i.n > 1:
    i.n -= 1; d = v - i.mu; i.mu -= d/i.n; i.m2 -= d*(v-i.mu)
  return v

def select(col, row, cut):
  if (v := row[col.at]) == "?": return v
  return (v <= cut) if "mu" in col else (v == cut)

# --- tree -----------------------------------------------------------
# bring back num.lo. returnthat lo, not the x value XXX
def Tree(data, uses=None):
  def bestcut(rows):
    yields = ((sc, (x.at, cut))
              for x in data.cols.x
              for cut,sc in (numcut if "mu" in x else symcut)(x,rows))
    return min(yields, default=(BIG, None))[1]

  def symcut(sym, rows):
    grand, d = Num(), {}
    for r in rows:
      v, y = r[sym.at], disty(data, r)
      if v != "?":
        add(grand, y)
        add(d.get(v) or d.setdefault(v, Num()), y)
    for v, n in d.items():
      if n.n >= the.leaf and (grand.n - n.n) >= the.leaf:
        yield v, (n.n * n.mu + (grand.n * grand.mu - n.n * n.mu)) / grand.n

  def numcut(num, rows):
    lhs, rhs = Num(), Num()
    xys = sorted((r[num.at], add(rhs, disty(data, r)), bin(num, r[num.at])) 
                 for r in rows if r[num.at] != "?")
    
    for j, (x, y, b) in enumerate(xys):
      if rhs.n < the.leaf: break # Safety check: stop if rhs is too small
      add(lhs, sub(rhs, y)) 
      if lhs.n >= the.leaf and rhs.n >= the.leaf and b != xys[j+1][2]:
        yield x, (lhs.n * lhs.mu + rhs.n * rhs.mu) / (lhs.n + rhs.n)

  def grow(rows):
    at, cut, kids = None, None, {}
    if len(rows) > the.leaf * 2:
      if tmp := bestcut(rows):
        at, cut = tmp
        col = data.cols.all[at]
        ok, no = [], []
        [(ok if select(col,r,cut) else no).append(r) for r in rows if r[at]!="?"]
        if ok and no:
          uses.add(at)
          kids = {True: grow(ok), False: grow(no)}
    return Obj(root=data, kids=kids, at=at, cut=cut,
               x=mids(clone(data, rows)),
               y=adds(disty(data, row) for row in rows))

  uses = uses or set()
  return grow(data.rows), uses

def treeLeaf(t, row):
  if not t.kids: return t
  what = select(t.root.cols.all[t.at], row, t.cut)
  return t if what == "?" else treeLeaf(t.kids[what], row)

def treeShow(t, lvl=0, pre=""):
  if lvl==0: print(f"{'':{the.Show}}    Score      N   "
                   f"[{', '.join([y.txt for y in t.root.cols.y])}]")
  s = f"{('| ' * lvl + pre):{the.Show}}"
  print(f"{s}: {o(t.y.mu):6} : {t.y.n:4} : {o([t.x[c.at] for c in t.root.cols.y])}")
  if t.kids:
    c = t.root.cols.all[t.at]
    for k in sorted(t.kids, reverse=True):
      if "mu" in c: s = f"{c.txt} <= {o(t.cut)}" if k else f"{c.txt} > {o(t.cut)}"
      else:         s = f"{c.txt} == {t.cut}"    if k else f"{c.txt} != {t.cut}"
      treeShow(t.kids[k], lvl + 1, s)

# --- cli ------------------------------------------------------------
def eg_h(_):    print(__doc__)
def eg__the(_): print(o(the))
def eg_s(n):    the.seed = n; random.seed(n)

def eg__tree(f):
  d = Data(csv(f))
  tree, _ = Tree(clone(d, shuffle(d.rows)[:50]))
  treeShow(tree)

def eg__test(f):
  d = Data(csv(f))
  m = len(d.rows) // 2
  Y = lambda r: disty(d, r)
  b4 = sorted(Y(r) for r in d.rows)
  win = lambda r: int(100 * (1 - (Y(r)-b4[0]) / (b4[m] - b4[0] + 1/BIG)))
  wins = Num()
  for _ in range(20): 
    rows = shuffle(d.rows)
    test, train = rows[m:], rows[:m][:the.Budget]
    tree, _ = Tree(clone(d, train))
    test.sort(key=lambda r: treeLeaf(tree, r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[m])} ,lo {o(b4[0])}",
        *[f"{s} {len(a)}" for s, a in 
          dict(x=d.cols.x, y=d.cols.y, r=d.rows).items()],
        *f.split("/")[-2:], sep=" ,")

if __name__ == "__main__":
  for j, s in enumerate(sys.argv):
    if f := vars().get(f"eg{s.replace('-', '_')}"):
      try: f(sys.argv[j + 1] if j + 1 < len(sys.argv) else None)
      except Exception: traceback.print_exc()
    elif (k := s.lstrip("-")[:1]) in the:
      the[k] = cast(sys.argv[j + 1]) if j+1 < len(sys.argv) else the[k]
