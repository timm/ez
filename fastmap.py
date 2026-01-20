#!/usr/bin/env python3 -B
import sys,random
from ez import DATA,csv,clone,mids,distx,adds,NUM

def report(data,groups,loud=False):
  C,stats=[],[]
  for g in groups:
    if len(g)<2:continue
    mu=mids(clone(data,rows=g))
    C.append(mu)
    stats+=[f"{adds((distx(data,r,mu)for r in g),NUM()).mu:.2f}"]
  if loud:print("Stats:",*sorted(stats))
  return C

def bisect(data,stop=None,loud=False):
  stop=stop or max(2,int(len(data.rows)**.5))
  def grow(rows,lvl=0):
    if len(rows)<=stop or lvl>=4:return[rows]
    p=random.choice(rows)
    l=max(rows,key=lambda r:distx(data,r,p))
    r=max(rows,key=lambda r:distx(data,r,l))
    L,R=[],[]
    for row in rows:
      d1,d2=distx(data,row,l),distx(data,row,r)
      (L if d1<d2 else R).append(row)
    if not L or not R:return[rows]
    return grow(L,lvl+1)+grow(R,lvl+1)

  return report(data,grow(data.rows),loud)

if __name__=="__main__":
  seed,file=sys.argv[1:]
  random.seed(int(seed))
  print(random.random())
  bisect(DATA(csv(file)),loud=True)
