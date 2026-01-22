jan 22

really shoulw relect 60 times

-----

# Knee Point Derivation for $1/\sqrt{n}$ Curve

Given the standard error curve $SE = \sigma/\sqrt{n}$, we find the "knee" — the point of maximum perpendicular distance from the line connecting endpoints.

## Setup

Endpoints: $(x_1, 1/\sqrt{x_1})$ to $(x_2, 1/\sqrt{x_2})$

Normalize to unit square:

$$u = \frac{x - x_1}{x_2 - x_1}, \quad v = \frac{1/\sqrt{x} - 1/\sqrt{x_2}}{1/\sqrt{x_1} - 1/\sqrt{x_2}}$$

The line from $(0,1)$ to $(1,0)$ has equation $u + v = 1$.

## Distance to Line

Perpendicular distance (ignoring constant $\sqrt{2}$):

$$d(x) = 1 - u - v$$

Let $A = x_2 - x_1$ and $B = 1/\sqrt{x_1} - 1/\sqrt{x_2}$

$$d(x) = 1 - \frac{x - x_1}{A} - \frac{1/\sqrt{x} - 1/\sqrt{x_2}}{B}$$

## Maximize

$$\frac{d}{dx}d(x) = -\frac{1}{A} + \frac{1}{2B \cdot x^{3/2}} = 0$$

Solving:

$$x^{3/2} = \frac{A}{2B}$$

$$x_{knee} = \left(\frac{A}{2B}\right)^{2/3}$$

## Simplify

Let $a = \sqrt{x_1}$, $b = \sqrt{x_2}$. Then:

$$A = b^2 - a^2 = (b-a)(b+a)$$

$$B = \frac{1}{a} - \frac{1}{b} = \frac{b-a}{ab}$$

$$\frac{A}{2B} = \frac{(b-a)(b+a)}{2} \cdot \frac{ab}{b-a} = \frac{ab(a+b)}{2}$$

$$\boxed{x_{knee} = \left(\frac{ab(a+b)}{2}\right)^{2/3}}$$

## Example

For $x_1 = 8$, $x_2 = 256$:

- $a = \sqrt{8} = 2\sqrt{2}$
- $b = \sqrt{256} = 16$
- $ab = 32\sqrt{2}$
- $a + b = 2\sqrt{2} + 16$

$$x_{knee} = \left(\frac{32\sqrt{2}(2\sqrt{2} + 16)}{2}\right)^{2/3} = \left(16\sqrt{2}(2\sqrt{2} + 16)\right)^{2/3}$$

$$= \left(64 + 256\sqrt{2}\right)^{2/3} \approx (426.04)^{2/3} \approx 56.6$$

<img width="859" height="554" alt="image" src="https://github.com/user-attachments/assets/e47a01eb-acdd-4ff1-8f94-c08bee381761" />



# results with 60 repeats;

colum1 is a score that should be maximizes. runs 0..100
r=#rows,y=#goals,x=#inputs

is r,y,x a good predictor for score?



```
  -b bins=5    Number of bins
   -B Budget=30  initial sampling budget 
   -C Check=5   final evalaution budget
   -l leaf=4    Min examples in leaf of tree
   -p p=2       Distance coeffecient
   -s seed=1    Random number seed
   -w width=30  Tree display width 
```


```
Thu Jan 22 18:02:04 EST 2026
[:bins 5 :Budget 50 :Check 5 :leaf 4 :p 2 :seed 1 :Show 30]
3 13 15 17 18 22 30 34 37 40 41 43 44 47 49 49 49 51 52 53 53 53
54 54 54 55 55 55 56 56 58 58 59 59 60 60 60 60 60 60 61 62 63 63
65 65 66 66 68 68 68 70 70 72 72 75 75 76 76 76 77 78 78 78 79 80
80 80 81 82 82 82 82 83 83 84 84 84 85 86 86 86 87 87 87 88 88 88
89 89 90 90 90 90 91 92 92 92 92 93 93 93 93 94 94 94 95 95 95 95
96 96 96 97 97 98 98 98 98 99 100 100 100 100 100 100 100
```

**Big finding: sd is the strongest predictor** (ρ = -0.58)

| Predictor | ρ | p |
|-----------|------|--------|
| **sd** | -0.58 | <0.001 |
| **y (goals)** | -0.47 | <0.001 |
| r (rows) | -0.17 | 0.057 |
| x (inputs) | -0.14 | 0.12 |

R² jumps from **0.21 → 0.36** when you add sd.

**But here's the catch:** sd is an *outcome*, not an *a priori* predictor. You only know sd after running experiments. It tells you "easy datasets have high scores AND low variance" — which is tautological.

For predicting score *before* running:
- **y (goals)** is still the only useful signal
- **x, r** remain useless

The sd finding does suggest something useful though: **if early runs show high variance, expect lower final scores**. Could be useful for early stopping or adaptive budget allocation.

FYI The Health-* datasets are the smoking gun:

**Same (x=5, y=3, r=10000), wildly different outcomes:**
- Health-ClosedPRs0008: score=3, sd=8
- Health-ClosedPRs0011: score=100, sd=0

What's different? The *landscape*, not the *shape*.

**Likely culprits:**

1. **Pareto front geometry** — Is it convex (easy) or concave/disconnected (hard)? Are good solutions clustered or scattered?

2. **Objective correlation** — Negatively correlated goals = harder tradeoffs. If goals align, optimization is trivial.

3. **Feature-objective mapping** — Linear? Smooth? Or rugged with local optima?

4. **Noise/variance** in the data itself — Some Health-* repos may just have noisier metrics.

**The sd correlation supports this.** High sd = optimizer struggles to converge = landscape is hard. But you can't know sd until you run experiments.

**Research direction:** Instead of (x,y,r), characterize datasets by:
- Objective correlation matrix
- Pareto front sparsity/convexity (sample and measure)
- Landscape ruggedness (fitness distance correlation)

These would actually predict difficulty. Your current metadata is like predicting marathon times from "number of legs" — necessary but nowhere near sufficient.

