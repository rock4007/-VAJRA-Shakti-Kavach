# Theory

Let $S(t)$ denote system stability with target invariant $S(t) \geq S_{min}$.

The controller enforces:

$$
\dot{V}(x) = \nabla V(x) f(x, u) \leq -\alpha \|x\|^2 + \Gamma\,\epsilon
$$

where $\Gamma$ is coupling strength and $\epsilon$ captures adversarial disturbance energy. Operationally, when $\Gamma$ rises, policy adaptation latency and consensus confidence must tighten to maintain negative drift in $V(x)$.
