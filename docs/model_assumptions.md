# Simulation assumptions and interpretation limits

## Observer

The action order is Fresh, Watch, Discount, Donate. The assumed error probability is `p0 + pmax / (1 + exp(-(ΔE00-midpoint)/scale))`, with `p0=0.01`, `pmax=0.39`, midpoint 8 and scale 3. Given an error, adjacent actions receive weight 0.70 and nonadjacent actions 0.15 before normalization. This is an illustrative monotone sensitivity function only. It is not fitted to participants, published recognition trials, or retail staff. Confusion matrices, estimated trigger rates and logit output are synthetic model outcomes. No human data were collected.

## Inventory and capacity

Each simulated day receives a Poisson number of arrivals (mean 80 initially). Half are red near-expiry donation-trigger items; the other half are evenly split among the other three action categories. Under perfect recognition, the configured action is applied. Under simulated recognition errors, each true category uses its own color's calculated ΔE00 to select its confusion row and category-level multinomial draw. The day's donation queue is limited to the configured capacity. False donation triggers and correctly recognized red items share the queue; queue allocation is sampled hypergeometrically. Overflow is offered for discount recovery. Discount recovery is Bernoulli with probability 0.55. Other unsaved arrivals expire. The model's horizon is 30 days; capacity scenarios are 10, 25, and 50 units/day; random seed is fixed in `config.json` and derived deterministically by illumination, recognition treatment and replicate, with shared seeds across capacity levels.

These are transparent alternative scenario parameters, not an implementation of Nigam's Near-Expiry model. Donation, discount recovery and expiry are coarse unit flows. `donated_units` includes all allocated donations, `true_donated_units` isolates eligible red items, and `false_donated_units` records false triggers that occupied donation capacity. Only true donations and recovered discounted items count toward `units_saved`. The model does not represent prices, product-specific shelf lives, routing, refrigeration, food-safety eligibility, or measured store operations.

## Sustainability

The reported alternative estimate is `saved units × 0.8 kg/unit × emissions factor (kg CO2e/kg)`. The central configured factor remains 2.5. Low-impact and high-impact sensitivity factors are 1.5 and 3.5 kg CO2e/kg (±40% around the central value). These are illustrative sensitivity bounds, not measured product footprints or literature-derived factors. The source note in `config.json` records that scope. This is not a life-cycle assessment, observed waste reduction, or Nigam score. `sustainability_analysis.csv` records each factor and the method note.

## Statistical outputs

The ΔE confidence interval is a descriptive t interval across the four fixed label colors for each illumination; it must not be generalized as a population interval. Trigger-rate Wilson intervals quantify Monte Carlo sampling around the configured synthetic observer model. Donation intervals are the 2.5th and 97.5th percentiles across fixed-seed Monte Carlo runs. The statsmodels logistic fit describes assumption-generated trial outcomes only; its p-values are intentionally not used to claim empirical significance.
