# <!-- vim: set ts=2 sw=2 sts=2 et: -->
from fileinput import FileInput as file_or_stdin
import re,sys,ast,math,random,inspect
from math import exp,log,cos,sqrt,pi
import re,sys,ast,math,random
from types import *

R   = random.random
one = random.choice

le = lambda x,y: x <= y
gt = lambda x,y: x >  y

def cdf(x,mu,sd):
  def cdf1(z): return 1 - 0.5*2.718**(-0.717*z - 0.416*z*z)
  z = (x - mu) / sd
  return cdf1(z) if z >= 0 else 1 - cdf1(-z)

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

def csv(file) -> Generator[row]:
  "Iteratively return rows in a csv"
  infile = sys.stdin if file=="-" else open(file)
  with infile as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def dot(s:str=".") -> None: 
  "print a character to standard error"
  print(s, file=sys.stderr, flush=True, end="")

def medianSd(a: list[number]) -> tuple[number,number]:
  "non parametric mid and div"
  a = sorted(a)
  return a[int(0.5*len(a))], (a[int(0.9*len(a))] - a[int(0.1*len(a))])

def nth(n): 
  "Return a function that returns the `n`-th idem."
  return lambda a:a[n]

# Rounding off
def r2(x): return round(x,2)
def r3(x): return round(x,3)

def timing(fun) -> number:
  "Return time to run a function."
  start = time()
  fun()
  return time() - start

def xval(lst:list, m:int=5, n:int=5, some:int=10**6) -> Generator[rows,rows]:
  "M-by-N cross val"
  for _ in range(m):
    random.shuffle(lst)
    for n1 in range (n):
      lo = len(lst)/n * n1
      hi = len(lst)/n * (n1+1)
      train, test = [],[]
      for i,x in enumerate(lst):
        (test if i >= lo and i < hi else train).append(x)
      train = random.choices(train, k=min(len(train),some))
      yield train,test 
