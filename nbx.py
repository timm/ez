#!/usr/bin/env python3 -B
"""
nbx.py: Naive Bayes Acquisition for Explainable Optimization
(c) 2026, MIT license

Theory: TPE (Bergstra 2011), BORE (Tiao 2021) — score ∝ P(x|best)/P(x|rest)

USAGE: python3 nbx.py [OPTIONS] FILE
OPTIONS:
  -B Budget=50 Labelling budget.
  -k k=1       Laplace smoothing for symbols.
  -m m=2       Prior smoothing for classes.
  -p p=2       Minkowski coefficient.
  -s seed=1    Random seed.
"""
import re,sys,math,random
from math import sqrt,exp,log,pi
BIG, the = 1e32, {}

# --- Utilities ---------------------------------------------------------------
def csv(f):
  with open(f) as file:
    for s in file: yield [cast(x) for x in s.split(",")]

def cast(s):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s.strip()

def o(t):
  match t:
   case dict(): return "{"+" ".join(f":{k} {o(t[k])}" for k in t)+"}"
   case float(): return f"{int(t)}" if int(t) == t else f"{t:.2f}"
   case tuple(): return "(" + ", ".join(o(x) for x in t) + ")"
   case list(): return "[" + ", ".join(o(x) for x in t) + "]"
   case _: return str(t)

class Obj(dict):
  __getattr__,__setattr__,__repr__=dict.__getitem__,dict.__setitem__,o

# --- Columns -----------------------------------------------------------------
def Sym(n=0,s=" "): return Obj(at=n,txt=s,n=0,has={})
def Num(n=0,s=" "): return Obj(at=n,txt=s,n=0,mu=0,m2=0,sd=0, goal=s[-1]!="-")
def Col(n=0, s=""): return (Num if s[0].isupper() else Sym)(n,s)

def add(i,v):
  if v == "?": return v
  i.n += 1
  if "mu" in i:
    d = v - i.mu; i.mu += d/i.n; i.m2 += d*(v - i.mu)
    i.sd = 0 if i.n < 2 else (i.m2/(i.n - 1))**.5
  else: i.has[v] = 1 + i.has.get(v,0)
  return v

# --- Data --------------------------------------------------------------------
def Cols(names):
  all = [Col(n,s) for n,s in enumerate(names)]
  x = [c for c in all if not re.search(r"[!+-X]$", c.txt)]
  y = [c for c in all if     re.search(r"[!+-]$",  c.txt)]
  return Obj(names=names, all=all, x=x, y=y)

def Data(items):
  data = Obj(rows=[], cols=None)
  for row in items:
    if data.cols: data.rows.append([add(c,x) for c,x in zip(data.cols.all,row)])
    else: data.cols = Cols(row)
  return data

def clone(data, rows=[]): return Data([data.cols.names] + rows)

# --- Bayes -------------------------------------------------------------------
def pdf(num,v):
  v = num.sd**2 + 1/BIG
  return (1/sqrt(2*pi*v)) * exp(-((v - num.mu)**2)/(2*v))

def like(col, v, prior):
  if "mu" in col:  return pdf(col,v)
  else: return (col.has.get(v,0) + the.k*prior) / (col.n + the.k)

def loglike(data, row, nall):
  prior = (len(data.rows) + the.m) / (nall + the.m*2)
  return log(prior) + sum(log(like(c, row[c.at], prior) + 1/BIG)
                          for c in data.cols.x if row[c.at] != "?")

def acquire(row, best, rest, nall):
  return loglike(best, row, nall) - loglike(rest, row, nall)

# --- Distance to Goals -------------------------------------------------------
def norm(num,x): return (x - num.mu) / (num.sd + 1/BIG)
def cdf(z):    return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))

def disty(data, row):
  n, d = 0, 0
  for c in data.cols.y:
    if (v := row[c.at])!="?": n,d = n+1, d+(cdf(norm(c,v)) - c.goal) ** the.p
  return (d/n) ** (1/the.p) if n else 0

# --- Explain -----------------------------------------------------------------
def explain(row, best, rest):
  print(f"\n{'Feature':<12} {'Value':<8} {'Best':<12} {'Rest':<12} {'Vote':>6}")
  print("-" * 52)
  for cb, cr in zip(best.cols.x, rest.cols.x):
    if (x := row[cb.at]) == "?": continue
    b, r = like(cb,x,0.5), like(cr,x,0.5)
    vote = log(b + 1/BIG) - log(r + 1/BIG)
    if abs(vote) < 0.1: continue
    if "mu" in cb:
      print(f"{cb.txt:<12} {x:<8.2f} {cb.mu:.2f}±{cb.sd:.2f}"
            f"   {o(cr.mu)}±{o(cr.sd)}   {vote:+.2f}")
    else:
      print(f"{cb.txt:<12} {str(x):<8} {o(b)}        {o(r)}        {vote:+.2f}")

# --- Main --------------------------------------------------------------------
def main(f):
  random.seed(the.seed)
  d = Data(csv(f))
  random.shuffle(d.rows)
  train, pool = d.rows[:the.Budget], d.rows[the.Budget:]
  train.sort(key=lambda r: disty(d,r))
  k    = int(len(train)**.5)
  best = clone(d, train[:k])
  rest = clone(d, train[k:])
  pool.sort(key=lambda r: acquire(r, best, rest, len(train)), reverse=True)
  print(f"Top acquire: {acquire(pool[0], best, rest, len(train)):+.2f}")
  print(f"Best: {len(best.rows)}, Rest: {len(rest.rows)}, Pool: {len(pool)}")
  explain(pool[0], best, rest)

# --- main ----------------------------------------------------------
def eg_h(_):    print(__doc__)
def eg__the(_): print(o(the))
def eg__sym(_): print(add(add(add(Sym(),"a"),"a"),"b"))
def eg__num(_): print([add(Num(), x) for x in [10,20,30,40]][-1])
def eg__csv(f): [print(r) for r in csv(f)]
def eg__opt(f): main(f)

the=Obj(**{k:cast(v) for k,v in re.findall(r"(\S+)=(\S+)",__doc__)})
if __name__ == "__main__":
  for j,s in enumerate(sys.argv):
    v = cast(sys.argv[j+1]) if j+1 < len(sys.argv) else None
    if f := vars().get(f"eg{s.replace('-', '_')}"): f(v)
    elif k := s.lstrip("-")[0] in the: the[k] = v
