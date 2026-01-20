#!/usr/bin/env python3 -B
import sys, math, random
from ez import csv,distx,disty,gauss,sd,pick,NUM,SYM,DATA,nearest, o

def sa(data, k=4000, m_rate=0.5, loud=False):
  LO, HI = {}, {}
  for c in data.cols.x:
    if c.it == NUM:
      LO[c.at],*_,HI[c.at] = sorted(r[c.at] for r in data.rows if r[c.at]!="?")

  def mutate(c, v):
    return pick(c.has,c.n) if c.it==SYM else (
      LO[c.at] + (gauss(v, sd(c)) - LO[c.at]) % (HI[c.at] - LO[c.at] + 1E-32))

  def score(row):
    near = nearest(data,row)
    for y in data.cols.y: row[y.at] = near[y.at]
    return disty(data, row)

  s = random.choice(data.rows)[:]
  e, best = score(s), s[:]

  for heat in range(k):
    sn = s[:]
    for c in random.choices(data.cols.x, k=max(1, int(m_rate*len(data.cols.x)))):
      sn[c.at] = mutate(c, sn[c.at])

    if (en:=score(sn)) < e or random.random() < math.exp((e - en)/(1 - heat/k)):
      s, e = sn, en
      if en < disty(data, best): 
        best = s[:]
        if loud: print(f"{heat:<5} {e:.3f}", o(best))

  return best

if __name__=="__main__":
  seed,file = sys.argv[1:]
  random.seed(seed)
  sa(DATA(csv(file)), loud=True)
