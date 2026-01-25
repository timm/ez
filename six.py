#!/usr/bin/env python3
"""
six.py: naive bayes classifier
(c) 2026, Tim Menzies, MIT license.

Options:
  -a alpha=5     Threshold for 'good'.
  -b budget=30   Evalaution budget.
  -c check=5     Final check.
  -k k=1         Bayes back for rare attributes.
  -m m=2         Bayes hack for rare classes.
  -p p=2         Distance coefficient
  -s seed=1      Random seed.
  --csv F        Print rows from CSV file. 
  --num          Test numeric column.
  --sym          Test symbolic column.
  --the          Print config settings. """

import re, sys, math, random
from math import sqrt, exp, log
BIG = 1E32
the={}

# --- create --------------------------------------------------------
def o(t):
  if isinstance(t, dict): t="{"+" ".join(f":{k} {o(t[k])}" for k in t)+"}"
  if isinstance(t,float): return f"{int(t)}" if int(t)==t else f"{t:.2f}"
  return str(t) 

class Obj(dict):
  __getattr__,__setattr__,__repr__=dict.__getitem__,dict.__setitem__,o

def Col(n=0, s=" "): return (Num if s[0].isupper() else Sym)(n,s)
def Sym(n=0, s=" "): return Obj(at=n, txt=s, n=0, has={})
def Num(n=0, s=" "): return Obj(at=n, txt=s, n=0, mu=0, m2=0,sd=0,
                               goal= s[-1] != "-")

def Data(s="", items=[]):
  d = Obj(txt=s, rows=[], cols=None)
  [add(d, row) for row in items]
  return d

def Cols(row):
  all=[Col(n,s) for n,s in enumerate(row)]
  return Obj(names=row, all=all,
             x=[c for c in all if not re.search(r"[+-X]$", c.txt)],
             y=[c for c in all if re.search(r"[+-]$", c.txt)])

# --- update --------------------------------------------------------
def add(i, v, inc=1):
  if "rows" in i: # Data
    if not i.cols: i.cols = Cols(v)
    else: 
      [add(c, v[c.at], inc) for c in i.cols.all]
      (i.rows.append if inc==1 else i.rows.remove)(v)
  elif v != "?":
    i.n += inc
    if "has" in i:  i.has[v] = inc + i.has.get(v, 0) # Sym
    else: 
      d = v - i.mu; i.mu += inc*d/i.n; i.m2 += inc*d*(v - i.mu) # Num
      i.sd = 0 if i.n < 2 else sqrt(max(i.m2,0)/(i.n - 1))
  return v

def norm(num,v): 
  z = (v - num.mu) / (num.sd + 1/BIG)
  return 1 / (1 + exp( -1.7 * max(-3, min(3, z))))

def disty(data, row):
  return minkowski((norm(y,row[y.at]) - y.goal) for y in data.cols.y)

# --- bayes ---------------------------------------------------------
def like(i, v, prior=0):
  if "has" in i:   # Sym
    n = i.has.get(v, 0) + the.k*prior
    tmp = max(1/BIG, n/(i.n + the.k + 1/BIG))
  else:             # Num
    var = i.sd**2 + 1/BIG
    tmp = (1/sqrt(2*math.pi*var)) * exp(-((v - i.mu)**2)/(2*var))
  return max(tmp,1/BIG)

def likes(i, r, nall, nh=2):
  b4 = (len(i.rows) + the.m)/(nall + the.m*nh)
  return log(b4) + sum(log(like(c, r[c.at], b4)) 
                       for c in i.cols.x if r[c.at] != "?")

def y(data):  return lambda row: disty(data,row)

def peek(rows):
  rows = list(rows)
  random.shuffle(rows)
  best,rest,both = None,None,None
  for n,row in enumerate(rows):
    if n > the.budget : break
    if n==0 : both = Data("all", [row]); continue
    add(both, row)
    if n == the.alpha : 
      tmp  = sorted(both.rows, key=y(both))
      print(tmp)
      best = Data("best", [both.cols.names] + tmp[:len(tmp)//2])
      rest = Data("rest", [both.cols.names] + tmp[len(tmp)//2:])
    elif n > the.alpha:
      pb = likes(best, row, n-1, 2)
      pr = likes(rest, row, n-1, 2)
      print(pb,pr)
      add(best if pb > pr else rest, row)
      if len(best.rows) > sqrt(n):
        best.rows.sort(key=y(best))
        add(rest, add(best, best.rows[-1]))
        print(len(best.rows), len(rest.rows))
  return sorted(best.rows, key=y(best))[:the.check]
 
# --- lib -----------------------------------------------------------
def cast(s):
  try: return int(s)
  except Exception: 
    try: return float(s)
    except Exception: return s.strip()

def csv(f): 
  return ([cast(x) for x in s.split(",")] for s in open(f))

def minkowski(items):
  n,d = 0,0
  for item in items: n, d = n+1, d+item ** the.p
  return 0 if n==0 else (d / n) ** (1 / the.p)

# --- main ----------------------------------------------------------
def eg_h(_):    print(__doc__)
def eg__the(_): print(o(the))
def eg__sym(_): print(add(add(add(Sym(),"a"),"a"),"b"))
def eg__num(_): print([add(Num(), x) for x in [10,20,30,40]][-1])
def eg__csv(f): [print(r) for r in csv(f)]
def eg__peek(f):[print(*x) for x in peek(csv(f))] 

the=Obj(**{k:cast(v) for k,v in re.findall(r"(\S+)=(\S+)",__doc__)})
if __name__ == "__main__":
  for j,s in enumerate(sys.argv):
    if f := vars().get(f"eg{s.replace('-', '_')}"):
      f(sys.argv[j+1] if j+1 < len(sys.argv) else None)
