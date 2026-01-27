#!/usr/bin/env python3 -B
"""
ezr.py: easy AI tools
(c)2026 Tim Menzies, MIT license.

Options:
   -p p=2   
   -s seed=1
"""
import re, sys, math, random, traceback
from math import sqrt, exp, log
BIG = 1E32
the = {}

# --- pretty print ---------------------------------------------------
def cast(s):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s.strip()

def csv(f):
  with open(f) as file:
    for line in file:
      line = re.sub(r'\s+', '', line.split("#")[0])
      if line: yield [cast(x) for x in line.split(",")]

def gauss(mu, sd1):
  return mu + 2 * sd1 * (sum(random.random() for _ in range(3)) - 1.5)

def pick(d, n):
  n *= random.random()
  for k, v in d.items():
    if (n := n - v) <= 0: break
  return k

def shuffle(lst): random.shuffle(lst); return lst

def o(t):
  match t:
    case dict(): return "{" + " ".join(f":{k} {o(t[k])}" for k in t) + "}"
    case float(): return f"{int(t)}" if int(t) == t else f"{t:.2f}"
    case list(): return "[" + ", ".join(o(x) for x in t) + "]"
    case tuple(): return "(" + ", ".join(o(x) for x in t) + ")"
    case _:  return str(t)

class Obj(dict):
  __getattr__,__setattr__,__repr__=dict.__getitem__,dict.__setitem__,o

# --- constructors ---------------------------------------------------
def Sym(n=0, s=" "): return Obj(at=n,txt=s,n=0,has={})
def Num(n=0, s=" "): return Obj(at=n,txt=s,n=0,mu=0,m2=0,goal=s[-1]!="-")
def Col(n=0, s=" "): return (Num if s[0].isupper() else Sym)(n, s)

def Cols(row):
  all = [Col(n, s) for n, s in enumerate(row)]
  return Obj(names=row, all=all,
             x=[c for c in all if not re.search(r"[+\-!X]$", c.txt)],
             y=[c for c in all if     re.search(r"[+\-!]$",  c.txt)])

def Data(src=None):
  i = Obj(n=0, rows=[], cols=None)
  if src: [add(i, r) for r in src]
  return i

def clone(i, rows=None): return Data([i.cols.names] + (rows or []))

def add(i, v):
  if "rows" in i:  # Data
    if not i.cols: i.cols = Cols(v)
    else: i.rows.append([add(c, v[c.at]) for c in i.cols.all])
  elif v != "?":
    i.n += 1
    if "mu" in i:  d = v - i.mu; i.mu += d / i.n; i.m2 += d * (v - i.mu)
    else: i.has[v] = 1 + i.has.get(v, 0)
  return v

def adds(src, i=None):
  i = i or Num()
  for v in src: add(i, v)
  return i

# --- query ----------------------------------------------------------
def mid(i):    return i.mu if "mu" in i else max(i.has, key=i.has.get)
def mids(i):   return [mid(c) for c in i.cols.all]
def spread(i): return sd(i)  if "mu" in i else ent(i)
def sd(i):     return 0 if i.n < 2 else sqrt(i.m2 / (i.n - 1))
def ent(i):    
 return -sum(p*log(p,2) for n in i.has.values() if (p:= n/i.n) > 0)

def z(i, v):  return (v - i.mu) / (sd(i) + 1 / BIG)
def norm(z): return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))

# --- distance -------------------------------------------------------
def minkowski(src):
  n, d = 0, 0
  for v in src: n, d = n + 1, d + v ** the.p
  return 0 if n == 0 else (d / n) ** (1 / the.p)

def disty(i, row):
  return minkowski(norm(z(c, row[c.at])) - c.goal for c in i.cols.y)

def distx(i, row1, row2):
  return minkowski(aha(c, row1[c.at], row2[c.at]) for c in i.cols.x)

def aha(i, u, v):
  if u == v == "?": return 1
  if "has" in i: return u != v
  u = "?" if u == "?" else norm(z(i, u))
  v = "?" if v == "?" else norm(z(i, v))
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

def furthest(i, row, rows):  return nearest(i, row, rows, max)
def nearest(i, row, rows, fn=min):  
  return fn(rows, key=lambda r: distx(i, row, r))

# --- cli ------------------------------------------------------------
def eg_h(_):    print(__doc__)
def eg__the(_): print(o(the))
def eg_s(n):    the.seed = n; random.seed(n)

def eg__sym(_):
  i = adds("aaaabbc", Sym())
  x = ent(i)
  print(o(x))
  assert abs(1.379 - x) < 0.05, "ent failed"

def eg__num(_):
  i = adds(gauss(10, 1) for _ in range(1000))
  print(Obj(mu=i.mu, sd=sd(i)))
  assert abs(10 - i.mu) < 0.05 and abs(1 - sd(i)) < 0.05, "num failed"

def eg__csv(f): [print(row) for row in list(csv(f))[::40]]

def eg__data(f):
  i = Data(csv(f))
  print(*i.cols.names)
  print(o(mids(i)))
  print(f"x: {[c.txt for c in i.cols.x]}")
  print(f"y: {[c.txt for c in i.cols.y]}")

def eg__clone(f):
  i = Data(csv(f))
  j = clone(i, i.rows[:10])
  print("original:", len(i.rows), "clone:", len(j.rows))
  print("cols match:", i.cols.names == j.cols.names)

def eg__spread(f):
  i = Data(csv(f))
  for c in i.cols.all:
    print(f"{c.txt:15} spread={o(spread(c)):8} mid={o(mid(c))}")

def eg__dist(f):
  i = Data(csv(f))
  r = i.rows[0]
  print("row0:", r)
  near = nearest(i, r, i.rows[1:])
  far = furthest(i, r, i.rows[1:])
  print("near:", near, "dist:", round(distx(i, r, near), 3))
  print("far: ", far, "dist:", round(distx(i, r, far), 3))

def eg__disty(f):
  i = Data(csv(f))
  for row in sorted(i.rows, key=lambda r: disty(i, r))[:5]:
    print(round(disty(i, row), 3), row)

# --- main -----------------------------------------------------------
the=Obj(**{k:cast(v) for k, v in re.findall(r"(\w+)=(\S+)", __doc__)})
random.seed(the.seed)

if __name__ == "__main__":
  for j, s in enumerate(sys.argv):
    if f := vars().get(f"eg{s.replace('-', '_')}"):
      try: f(sys.argv[j + 1] if j + 1 < len(sys.argv) else None)
      except Exception: traceback.print_exc()
    elif (k := s.lstrip("-")[:1]) in the:
      the[k] = cast(sys.argv[j + 1]) if j+1<len(sys.argv) else the[k]
