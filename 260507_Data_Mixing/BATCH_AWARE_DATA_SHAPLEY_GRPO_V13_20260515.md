# Batch-Aware Data Shapley for Taylor-Guided GRPO Sampling

Date: 2026-05-15

This note rewrites the local utility definition from **Data Shapley in One Training Run** into the batch-aware form we plan to implement for V13. The key change is simple: the original formulation assigns a local utility to a subset \(S\) after a training update has happened; our formulation uses the same Taylor logic to score a future GRPO batch \(B\), then converts the score into the next-batch sampling policy.

References:

- Data Shapley in One Training Run: <https://arxiv.org/abs/2406.11011>
- OpenReview page: <https://openreview.net/forum?id=HD6bWcj87Y>

## 1. Original Local Utility in Data Shapley

For one validation example \(z^{(\mathrm{val})}\), Data Shapley in One Training Run defines the local utility of a training subset \(S\) at training step \(t\) as

$$
U^{(t)}(S)
=
\ell(\tilde w_{t+1}(S), z^{(\mathrm{val})})
-
\ell(w_t, z^{(\mathrm{val})}),
$$

where:

- \(w_t\) is the model parameter before the current update.
- \(\tilde w_{t+1}(S)\) is the hypothetical parameter after updating with subset \(S\).
- \(\ell(w,z^{(\mathrm{val})})\) is the validation loss on \(z^{(\mathrm{val})}\).
- \(U^{(t)}(S)<0\) means subset \(S\) reduces validation loss, so it is useful.

Using a second-order Taylor expansion at \(w_t\), the local utility becomes

$$
U^{(t)}(S)
\approx
\nabla \ell(w_t,z^{(\mathrm{val})})^\top
(\tilde w_{t+1}(S)-w_t)
+
\frac{1}{2}
(\tilde w_{t+1}(S)-w_t)^\top
H_t^{(z^{(\mathrm{val})})}
(\tilde w_{t+1}(S)-w_t),
$$

where \(H_t^{(z^{(\mathrm{val})})}=\nabla_w^2\ell(w_t,z^{(\mathrm{val})})\). The first term measures whether the update direction aligns with validation loss reduction. The second term measures curvature cost along that update direction.

## 2. Our Batch-Aware GRPO Utility

In GRPO training, the unit of action is not a single already-finished update. At step \(t\), we must decide which future batch \(B\) should be sampled. Let the current policy be \(\pi_{\theta_t}\), and let the candidate batch \(B\) induce the GRPO gradient

$$
g_B^{\mathrm{GRPO}}
=
\frac{1}{|B|}
\sum_{i\in B}
g_i,
\qquad
g_i
=
\nabla_\theta
\ell_i^{\mathrm{GRPO}}(\theta_t).
$$

The hypothetical one-step update produced by batch \(B\) is

$$
\tilde\theta_{t+1}(B)
=
\theta_t
-
\eta g_B^{\mathrm{GRPO}},
$$

where \(\eta\) is the learning rate. We define a target-anchor loss

$$
\mathcal L_{\mathcal A}(\theta)
=
\mathbb E_{z\sim\mathcal A}
[
\ell(\theta,z)
],
$$

where \(\mathcal A\) is a fixed anchor set used only to estimate target direction. In implementation this anchor should be prompt-only / training-derived, not a test-answer leakage source.

Following the original Data Shapley local utility, the batch-level loss change is

$$
U_B^{(t)}(B)
=
\mathcal L_{\mathcal A}(\tilde\theta_{t+1}(B))
-
\mathcal L_{\mathcal A}(\theta_t).
$$

Substituting \(\tilde\theta_{t+1}(B)-\theta_t=-\eta g_B^{\mathrm{GRPO}}\) into the Taylor expansion gives

$$
U_B^{(t)}(B)
\approx
-
\eta
\nabla_\theta\mathcal L_{\mathcal A}(\theta_t)^\top
g_B^{\mathrm{GRPO}}
+
\frac{\eta^2}{2}
(g_B^{\mathrm{GRPO}})^\top
H_{\mathcal A}(\theta_t)
g_B^{\mathrm{GRPO}}.
$$

Because lower loss change is better, we use the negative local utility as the batch reward:

$$
J_t(B)
=
-
U_B^{(t)}(B)
\approx
\eta
a_t^\top g_B^{\mathrm{GRPO}}
-
\frac{\eta^2}{2}
(g_B^{\mathrm{GRPO}})^\top
H_{\mathcal A}(\theta_t)
g_B^{\mathrm{GRPO}},
$$

where

$$
a_t
=
\nabla_\theta\mathcal L_{\mathcal A}(\theta_t).
$$

Interpretation:

- The first-order term \(\eta a_t^\top g_B^{\mathrm{GRPO}}\) rewards a batch whose GRPO gradient points toward target-anchor improvement.
- The second-order term \(-\frac{\eta^2}{2}g_B^\top H_{\mathcal A}g_B\) penalizes risky or redundant update directions with high curvature cost.
- \(J_t(B)\) is not an explanation score after training; it is a decision score before constructing the next batch.

## 3. Low-Dimensional Sketch Version for Implementation

The full gradient and Hessian are too expensive. V13 therefore uses a fixed projection / sketch space.

Let

$$
z_i=P g_i,
\qquad
z_B
=
\frac{1}{|B|}
\sum_{i\in B}
z_i,
$$

where:

- \(P\) is a fixed random projection or fixed parameter-subspace sketch.
- \(z_i\in\mathbb R^m\) is the gradient sketch of sample \(i\).
- \(z_B\) is the average sketch of batch \(B\).

We approximate the target gradient and target Hessian in the same sketch space:

$$
\bar z_{\mathcal A}
\approx
P\nabla_\theta\mathcal L_{\mathcal A}(\theta_t),
\qquad
C_t
\approx
P H_{\mathcal A}(\theta_t)P^\top.
$$

In code, \(C_t\) is a PSD curvature proxy estimated from shadow-anchor gradient sketches, for example by an EMA covariance / second-moment matrix. The implementable batch utility becomes

$$
J_t(B)
\approx
\eta
\bar z_{\mathcal A}^{\top}
z_B
-
\frac{\eta^2}{2}
z_B^\top
C_t
z_B.
$$

This is the direct batch-aware counterpart of the Data Shapley Taylor utility.

## 4. From Batch Utility to Sample-Level Marginal Selection

The important batch-aware part is that the value of a candidate sample depends on what has already been selected into the current batch. Suppose we are constructing a batch sequentially. Let \(B_k\) be the partial batch after \(k\) samples have been selected.

For readability, absorb the fixed final-batch normalization into \(z_i\). The marginal gain of adding candidate sample \(i\) is

$$
\Delta_i^{(t)}(B_k)
=
J_t(B_k\cup\{i\})
-
J_t(B_k).
$$

Expanding the quadratic term gives

$$
\Delta_i^{(t)}(B_k)
\approx
\eta
\bar z_{\mathcal A}^{\top}
z_i
-
\frac{\eta^2}{2}
z_i^\top C_t z_i
-
\eta^2
z_i^\top C_t z_{B_k}.
$$

Equivalently,

$$
\Delta_i^{(t)}(B_k)
\approx
\underbrace{
\eta \bar z_{\mathcal A}^{\top}z_i
}_{\text{target alignment}}
-
\underbrace{
\frac{\eta^2}{2}z_i^\top C_tz_i
}_{\text{self curvature risk}}
-
\underbrace{
\eta^2 z_i^\top C_tz_{B_k}
}_{\text{interaction with selected batch}}.
$$

This is the concrete difference from static data valuation. A sample is not assigned one fixed score for the whole step. Its score changes as the partial batch \(B_k\) changes.

## 5. Sampling Policy

Within a selected domain \(d\), let \(\mathcal C_d\) be the candidate pool. The sample-level policy is

$$
\mu_t(i\mid d,B_k)
=
\frac{
\exp(\Delta_i^{(t)}(B_k)/\tau_s)
}{
\sum_{j\in\mathcal C_d}
\exp(\Delta_j^{(t)}(B_k)/\tau_s)
},
\qquad
i\in\mathcal C_d,
$$

where \(\tau_s\) is the sample-level temperature. The final sampler combines domain-level budget and sample-level batch-aware selection:

$$
\pi_t(i\mid B_k)
=
p_t(d_i)
\cdot
\mu_t(i\mid d_i,B_k).
$$

Here \(p_t(d)\) can remain the V11/V13 macro controller based on domain alignment, reward dynamics, and minimum budget constraints. The new part is \(\mu_t(i\mid d,B_k)\), which turns Taylor utility into a sequential batch construction policy.

## 6. Relation to the Original Formula

| Component | Data Shapley in One Training Run | Our batch-aware GRPO version |
| --- | --- | --- |
| Object being scored | A subset \(S\) in one training iteration | A future GRPO batch \(B\), or a candidate sample \(i\) given partial batch \(B_k\) |
| Update parameter | \(\tilde w_{t+1}(S)-w_t\) | \(\tilde\theta_{t+1}(B)-\theta_t=-\eta g_B^{\mathrm{GRPO}}\) |
| Evaluation target | Validation example \(z^{(\mathrm{val})}\) | Target / shadow anchor distribution \(\mathcal A\) |
| First-order term | \(\nabla\ell(w_t,z^{val})^\top\Delta w_S\) | \(\eta\bar z_{\mathcal A}^\top z_B\) or \(\eta\bar z_{\mathcal A}^\top z_i\) |
| Second-order term | \(\frac12\Delta w_S^\top H\Delta w_S\) | \(-\frac{\eta^2}{2}z_B^\top C_tz_B\), with marginal self and interaction risks |
| Output | Attribution / Shapley value for data contribution | Sampling probability for constructing the next batch |

## 7. Implementation Contract for V13

The planned implementation should satisfy the following contract.

1. For each candidate sample \(i\), compute or cache a GRPO-compatible gradient sketch \(z_i\), not only a representation embedding.
2. Maintain a fixed shadow-anchor set \(\mathcal A\) and compute \(\bar z_{\mathcal A}\) from the same sketch space.
3. Maintain a PSD curvature proxy \(C_t\), preferably via EMA of anchor sketch second moments.
4. Build each batch sequentially. After selecting sample \(i\), update the partial aggregate \(z_{B_k}\), then recompute marginal gains for the next selection step.
5. Use softmax sampling rather than deterministic top-k:

$$
\mu_t(i\mid d,B_k)\propto \exp(\Delta_i^{(t)}(B_k)/\tau_s).
$$

6. Log the decomposed terms:

$$
\eta\bar z_{\mathcal A}^\top z_i,\quad
z_i^\top C_tz_i,\quad
z_i^\top C_tz_{B_k},\quad
\Delta_i^{(t)}(B_k),\quad
\mu_t(i\mid d,B_k).
$$

These logs are necessary to prove that sampling is actually changing with the batch interaction term, rather than behaving like a fixed per-sample ranking.

## 8. Short Paper-Style Description

Starting from the local utility in Data Shapley in One Training Run, we reinterpret the coalition \(S\) as a future GRPO batch \(B\). A batch induces a policy-gradient update \(g_B^{\mathrm{GRPO}}\), and the second-order Taylor expansion of the target-anchor loss predicts whether this update will reduce the target risk. We then negate the predicted loss change to obtain a batch utility \(J_t(B)\). To make the objective implementable, both the target gradient and Hessian are approximated in a low-dimensional gradient-sketch space. Unlike static data valuation, our method uses the marginal gain \(J_t(B_k\cup\{i\})-J_t(B_k)\), so each sample's score depends on the partial batch already selected. This converts Taylor-based data valuation into a batch-aware data policy for future GRPO sampling.
