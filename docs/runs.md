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



# results with 20 repeats;

colum1 is a score that should be maximizes. runs 0..100
r=#rows,y=#goals,x=#inputs

is r,y,x a good predictor for score?

Let me analyze this quickly.**Short answer: No.** R² ≈ 0.2 — these explain only 20% of variance.

**What matters:**
- **y (goals)**: Only significant predictor (ρ = -0.47, p < 0.0001). More goals → harder → lower scores. Makes sense.
- **x (inputs)**: Not significant (p = 0.21). Surprising — dimensionality doesn't hurt much.
- **r (rows)**: Borderline (p = 0.06). More data doesn't reliably help.

The real story is probably in the *data characteristics* not captured here — class imbalance, feature correlations, noise levels, Pareto front shape. The Health-* datasets all have identical (x=5, y=3, r=10000) yet scores range from 3 to 100.


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
Bins =7, checks=5
3 17 17 18 21 29 29 31 37 39 40 42 43 45 48 48 48 50 50 50 50 52
52 52 52 53 53 53 55 55 55 55 56 56 56 56 57 58 59 60 61 61 62 62
63 65 65 66 66 67 67 68 68 70 71 73 73 73 74 75 76 76 76 77 78 78
79 79 80 82 83 83 84 84 84 85 85 85 85 85 85 86 86 86 88 88 89 89
89 90 90 90 90 90 91 91 92 92 92 92 92 93 93 94 94 95 95 95 96 96
96 97 97 97 97 98 98 98 98 99 100 100 100 100 100 100 100

Bins =7, checks=3
0 9 11 15 16 16 20 29 32 33 35 36 36 37 38 38 39 39 39 40 41 41 42
44 46 47 47 47 47 47 47 48 49 49 50 51 53 53 54 54 55 55 56 56 56
57 58 59 60 61 62 62 63 63 64 64 64 64 65 66 67 69 69 70 70 70 71
71 72 72 72 73 74 75 76 76 76 77 78 79 80 80 81 81 82 83 83 84 85
85 85 85 86 86 86 87 88 88 89 89 90 90 90 90 92 93 93 93 94 95 95
95 95 96 96 97 98 98 98 98 100 100 100 100 100 100 100

Bins =7, checks=4
0 12 16 17 17 17 22 29 34 36 37 39 43 43 44 45 46 47 47 47 48 48
50 51 51 51 52 52 53 53 53 55 56 56 57 57 59 59 59 59 61 61 63 64
64 64 65 65 65 66 67 68 68 68 68 69 69 70 71 72 72 73 74 75 75 76
76 76 78 78 78 78 80 80 80 80 80 81 82 82 82 83 84 85 85 86 86 87
87 88 89 89 89 89 89 90 90 91 91 91 92 93 93 93 94 94 94 94 94 95
95 96 96 96 97 97 98 98 98 99 100 100 100 100 100 100 100

BINGS=5 hecks=5
3 17 17 17 20 21 29 31 36 36 39 42 44 47 48 48 50 50 51 52 52 52
52 53 54 54 55 55 55 57 59 59 60 60 61 61 61 62 62 63 64 65 66 68
69 70 70 70 71 71 72 72 72 72 73 73 74 74 75 75 76 77 78 78 79 79
80 81 81 82 82 82 82 83 84 84 84 84 85 85 85 85 86 87 88 88 88 90
90 90 90 90 91 92 92 92 92 93 93 93 93 94 94 94 95 95 95 95 95 96
96 96 96 97 97 98 98 98 98 99 100 100 100 100 100 100 100

BINS=3 hecks=5
2 15 17 17 21 29 32 36 36 43 44 44 46 47 48 48 49 51 51 52 52 52
53 53 54 55 55 55 57 59 60 60 61 61 61 61 62 62 62 64 64 65 65 66
66 66 66 67 68 70 72 73 73 74 74 74 75 75 76 76 76 77 77 79 79 80
81 81 82 82 82 83 83 83 83 84 84 85 85 85 86 86 86 86 88 88 89 89
89 90 90 90 90 90 90 91 92 92 92 94 94 95 95 95 95 95 96 96 96 96
96 96 96 97 97 97 98 98 98 98 99 100 100 100 100 100 100

BINS=2 hecks=5
0 13 15 17 18 21 25 32 37 41 43 43 43 46 48 48 49 49 49 52 52 52
53 53 53 54 55 55 57 58 59 59 61 61 61 62 62 62 65 66 66 66 66 67
68 68 68 68 70 70 71 73 73 73 74 74 74 76 76 76 77 77 77 77 77 77
78 78 80 81 82 82 82 83 83 84 85 85 85 85 85 85 85 85 86 86 86 87
87 88 88 88 89 89 89 90 90 91 91 91 92 92 92 94 95 95 95 95 96 96
96 96 97 97 97 98 98 98 98 99 100 100 100 100 100 100 100

Bins=5, chec=5,budget=30
1 11 12 16 25 25 27 29 37 38 40 40 41 44 44 46 46 46 47 48 49 50
50 50 50 51 51 52 52 52 53 55 55 55 55 55 56 56 57 58 58 60 61 63
64 64 65 65 65 66 67 68 68 69 70 70 70 71 71 71 72 72 74 74 75 75
76 76 77 77 79 79 80 81 81 81 82 82 83 83 83 83 83 84 84 84 85 85
85 85 86 86 86 86 87 87 88 89 89 90 90 91 92 92 93 93 93 93 94 94
95 95 96 96 96 96 97 98 98 99 100 100 100 100 100 100 100

Bins=5, chec=5,budget=12
2 12 14 15 15 26 29 30 31 32 34 35 35 36 37 38 38 38 39 39 40 41
41 42 42 42 43 43 44 44 45 46 47 48 50 50 50 51 51 52 52 52 53 54
54 55 56 56 57 58 61 61 61 61 61 61 61 63 64 64 64 64 65 65 65 66
66 67 67 67 69 70 71 71 72 72 72 73 74 74 74 75 75 76 76 77 77 78
78 78 78 79 80 82 82 82 83 83 83 83 83 83 84 84 86 86 87 87 88 88
88 89 89 90 90 90 90 91 91 92 93 93 95 96 97 100 100

Bins=5, chec=5,budget=20
-345381173658630070302088494055424 1 14 16 17 21 28 29 31 36 36 37
40 40 41 42 42 43 44 44 44 45 45 46 46 46 46 47 47 48 48 49 49 49
49 50 51 52 54 54 56 56 57 57 58 59 62 63 63 63 64 64 65 67 67 67
69 69 69 69 70 70 70 70 70 71 73 74 75 75 75 75 76 76 77 78 78 78
79 79 80 80 80 80 80 81 81 82 82 82 82 83 83 84 85 85 85 86 86 86
86 87 87 88 88 90 90 91 91 93 94 94 95 95 96 96 96 97 98 98 98 99
100 100 100 100 100
```


