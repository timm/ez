# tree
def Tree(data, uses=None):
  uses = uses or set()
  def bestcut(rows):
    d={}
    for r in rows:
      y = disty(data,r)
      for col in data.cols.x:
        k = (col.at, bucket(col, r[col.at]))
        if k not in d: d[k] = NUM()
        add(d[k], y)
    return min(d.items(), key=lambda x: score(x[1]), default=None)

  def grow(rows):
    at, b, kids = None, None, {}   
    if len(rows) > the.leaf*2:
      if cut := bestcut(rows):
        ((at,b), _) = cut
        ok, no = [], []
        for r in rows:
          (ok if b == bucket(data.cols.all[at], r[at]) else no).append(r)
        if ok and no:
          uses.add(at)
          kids = {True:grow(ok), False:grow(no)}
    return obj(root=data, kids=kids, at=at, bucket=b,
               x= mids(clone(data,rows)),
               y= adds(disty(data,row) for row in rows))

  return grow(data.rows), uses

def treeLeaf(tree, row):
  if not tree.kids: return tree
  col = tree.root.cols.all[tree.at]
  what = bucket(col, row[col.at]) == tree.bucket
  return treeLeaf(tree.kids[what], row)

def treeShow(t):
  def show(n, lvl, pre):
    g = [n.x[c.at] for c in n.root.cols.y]
    print(f"{('| '*(lvl-1)+pre):{the.Show}}: {o(n.y.mu):6} : {n.y.n:4} : {o(g)}")
    for k in sorted(n.kids or {}, reverse=True):
      c, b = n.root.cols.all[n.at], n.bucket
      if SYM is c.it: s = f"{c.txt} {'==' if k else '!='} {b}"
      else:
        lo, hi = tekcub(c, b)
        if k: s=f"{c.txt}<{o(hi)}" if lo==-BIG else (f"{c.txt}>={o(lo)}"
                if hi==BIG else f"{o(lo)}<={c.txt}<{o(hi)}")
        else: s=f"{c.txt}>={o(hi)}" if lo==-BIG else (f"{c.txt}<{o(lo)}"
                if hi==BIG else f"{c.txt}<{o(lo)} or >={o(hi)}")
      show(n.kids[k], lvl+1, s)
  ys = ', '.join([y.txt for y in t.root.cols.y])
  print(f"{'':{the.Show}}   Score      N   [{ys}]"); show(t, 0, "")


