Chapter 1 — First-order ODEs & slope fields.

Big idea: a first-order ODE y' = f(x, y) gives a *rule for the slope* at every
point of the plane, not a single solution. Drawing a short arrow of slope
f(x, y) on a grid produces the SLOPE FIELD — a picture of the flow that every
solution must stay tangent to.

Worked equation: the logistic model
    y' = a*y*(1 - y/K)
with growth rate a and carrying capacity K. Its equilibria (where y' = 0) are
y = 0 and y = K; there the slope is zero and the field goes flat (horizontal
stripes). Stability depends on the sign of a: for a > 0, y = K attracts and
y = 0 repels; for a < 0 the roles flip.

What the learner sees on screen:
- A slope field that redraws as they drag sliders for a, K, and the initial
  condition y0.
- A red solution curve through y(0) = y0 bending to follow the flow.
- A time animation tracing y(t) as t advances from 0 to 10.

"Try it" exercises:
1. Set a < 0: which equilibrium becomes the attractor, which repels?
2. Start with y0 above K: does it fall to K or overshoot?
3. Find a K where a solution from y0 = 0.5 barely moves — what does that say
   about the slope near y = 0?
4. Push a toward 2: how does the steepness of the climb to K change?
