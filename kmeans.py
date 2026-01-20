#!/usr/bin/env python3 -B
import sys, random
from ez import DATA,csv,distx,clone,mids,adds

def kmeans(data, k=14, steps=10, loud=False):
  centroids = random.choices(data.rows, k=k)
  
  for step in range(steps):
    groups = [[] for _ in range(k)]
    for row in data.rows:
      c = min(range(k), key=lambda i: distx(data, row, centroids[i]))
      groups[c].append(row)
    
    stats = []
    for i in range(k):
      if groups[i]:
        errors = adds(distx(data, r, centroids[i]) for r in groups[i])
        stats.append(f"{errors.mu:.2f}")
        centroids[i] = mids(clone(data, rows=groups[i]))
    
    if loud: print(f"STEP {step}:", *stats)
  
  return centroids

if __name__ == "__main__":
  seed,file = sys.argv[1:]
  random.seed(int(sys.argv[1]))
  kmeans(DATA(csv(sys.argv[2])), loud=True)
