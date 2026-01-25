#!/usr/bin/env python3
"""
nb.py: naive bayes classifier
(c) 2026, Tim Menzies, MIT license.

USAGE
   python3 nb.py [OPTIONS] [FILE]

DESCRIPTION
    Incremental naive bayes. Training and testing are interleaved: after
    burn-in, each row is classified then added to the training set.

OPTIONS
    -h          Show help.
    -k k=1      Bayes low frequency hack for symbolic attributes.
    -m m=2      Bayes low frequency hack for class priors.
    -w wait=5   Start classifying after seeing "some" rows

EXAMPLES
    --the       Print config settings.
    --sym       Test symbolic column.
    --num       Test numeric column.
    --csv F     Print rows from CSV file.
    --nb F      Run naive bayes on CSV file.

INPUT FORMAT
    Comma-separated values. First row defines column names. Uppercase
    names (Age, Weight) are numeric; lowercase (name, color) are symbolic.
    Suffixes: "!" class label, "X" ignore.
    Missing values: "?".

----------------------------------------------------------------------
CODING STANDARD

  Type Hints (single letter)
    i:instance(Obj)   t:target(dict)   s:string    n:number
    r:row(list)       c:col(Obj)       v:value     f:file/filename
    d:delta/data      k:class/key      b4:before(prior)

  Class System
    Obj(dict):        Base class, provides dot notation access (d.x).
    CamelCase(args):  Factory functions (Sym, Num, Data) returning Obj.
    camelcase:        "data" (or e.g. "data1") is created by Data()

----------------------------------------------------------------------
API

  # Constructors
  Sym(n = 0, s = "")   -- Create symbolic column at position n, name s.
  Num(n = 0, s = "")   -- Create numeric column at position n, name s.
  Data(s = "", items = []) -- Create dataset from list of rows/items.
  clone(d, rows = [])  -- Create new Data with same structure as d.
  Cols(row)            -- Generate column headers from a list of names.

  # Classifier
  nb(items)           -- Run incremental Naive Bayes on item iterator.

  # Methods (Functional)
  add(i, v)           -- Update counts (Sym) or Welford stats (Num).
                      -- If i is Data, add row and update cols.
  like(i, v, prior)   -- Calculate likelihood of v given column i.
  likes(i, r, nall, nh)-- Calculate log-likelihood of row r given Data i.

  # Utilities
  cast(s)           -- Parse string to int, float, or strip whitespace.
  csv(file)           -- Iterator yielding rows from CSV file.
  o(t)                -- Pretty print object/dict t.
"""

import re, sys, math
from math import sqrt, exp, log
BIG = 1E32
the={}

# --- functions ------------------------------------------------------
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
   case list()|tuple(): return str([o(x) for x in t])
   case _: return str(t)

class Obj(dict):
  __getattr__,__setattr__,__repr__=dict.__getitem__,dict.__setitem__,o

# --- objects ------------------------------------------------------
def Sym(n=0, s=""): return Obj(at=n, txt=s, n=0, has={})
def Num(n=0, s=""): return Obj(at=n, txt=s, n=0, mu=0, m2=0)
def Col(n=0, s=""): return (Num if s[0].isupper() else Sym)(n,s)

def Data(s="", items=[]):
  d = Obj(txt=s, rows=[], cols=None)
  [add(d, r) for r in items]
  return d

def Cols(row):
  all = [Col(n,s) for n,s in enumerate(row)]
  return Obj(names=row, all=all,
             x=[c for c in all if not re.search(r"[!X]$", c.txt)],
             y=[c for c in all if re.search(r"!$", c.txt)])

def add(i, v):
  if "rows" in i: # Data
    if not i.cols: i.cols = Cols(v)
    else: i.rows.append([add(c, v[c.at]) for c in i.cols.all])
  elif v != "?":
    i.n += 1
    if "mu" in i: d = v - i.mu; i.mu += d/i.n; i.m2 += d*(v - i.mu) 
    else: i.has[v] = 1 + i.has.get(v, 0) # Sym
  return v

# --- bayes ---------------------------------------------------------
def like(i, v, prior=0):
  if "mu" in i: # Num
    sd = 0 if i.n < 2 else (i.m2/(i.n - 1))**.5
    var = sd**2 + 1/BIG
    return (1/sqrt(2*math.pi*var)) * exp(-((v - i.mu)**2)/(2*var))
  else:    # Sym
    n = i.has.get(v, 0) + the.k*prior
    return max(1/BIG, n/(i.n + the.k + 1/BIG))

def likes(i, r, nall, nh):
  b4 = (len(i.rows) + the.m)/(nall + the.m*nh)
  return log(b4) + sum(log(like(c, r[c.at], b4)) 
                       for c in i.cols.x if r[c.at] != "?")

def nb(rows):
  all, klasses, nh, out = None, {}, 0, Sym()
  for n, row in enumerate(rows):
    if n==0: all = Data("all", [row])
    else:
      k = row[all.cols.y[0].at]
      if k not in klasses: nh +=1; klasses[k]=Data(k,[all.cols.names])
      if (n - 1) > the.wait: 
        fn = lambda cat:likes(klasses[cat],row,n-1,nh)
        add(out, (max(klasses, key=fn), k)) #(predicted, actual)
      add(klasses[k], row)
  return out

# --- main ----------------------------------------------------------
def eg_h(_):    print(__doc__)
def eg__the(_): print(o(the))
def eg__sym(_): print(add(add(add(Sym(),"a"),"a"),"b"))
def eg__num(_): print([add(Num(), x) for x in [10,20,30,40]][-1])
def eg__csv(f): [print(r) for r in csv(f)]
def eg__nb(f):  [print(n,*x) for x,n in nb(csv(f)).has.items()] 

the=Obj(**{k:cast(v) for k,v in re.findall(r"(\S+)=(\S+)",__doc__)})
if __name__ == "__main__":
  for j,s in enumerate(sys.argv):
    if f := vars().get(f"eg{s.replace('-', '_')}"):
      f(sys.argv[j+1] if j+1 < len(sys.argv) else None)
