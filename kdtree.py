#!/usr/bin/env python3 -B
import sys,random
from ez import DATA, csv, clone, mids, distx, adds, NUM

def report(data, groups, loud=False):
  C, stats = [], []
  for g in groups:
    if not g: continue
    mu = mids(clone(data, rows=g))
    C.append(mu)
    stats += [f"{adds((distx(data, r, mu) for r in g), NUM()).mu:.2f}"]
  if loud: print("Stats:", *sorted(stats))
  return C

def kdtree(data, stop=None, loud=False):
  if stop is None: stop = len(data.rows)/8
  def grow(rows, lvl=0):
    if len(rows) < stop: return [rows]
    c = data.cols.x[lvl % len(data.cols.x)]
    # Tuple sort: False(0) < True(1). Puts values first, '?' last.
    rows.sort(key=lambda r: (r[c.at]=="?", r[c.at]))
    m = len(rows) // 2
    return grow(rows[:m], lvl+1) + grow(rows[m:], lvl+1)
  return report(data, grow(data.rows), loud)

if __name__=="__main__":
  seed,file = sys.argv[1:]
  random.seed(seed)
  print(random.random())
  kdtree(DATA(csv(file)), loud=True)
