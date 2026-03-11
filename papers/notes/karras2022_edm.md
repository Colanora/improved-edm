# karras2022_edm

- Frozen variants:
  - `euler`: upstream `ablation_sampler(..., solver='euler', discretization='edm', schedule='linear', scaling='none', S_churn=0)`
  - `heun`: upstream `edm_sampler(..., S_churn=0)`
- Equations used:
  - `d(x, sigma) = (x - D(x, sigma)) / sigma`
  - Euler step: `x_next = x_hat + (t_next - t_hat) d_cur`
  - Heun correction: `x_next = x_hat + (t_next - t_hat) * 0.5 * (d_cur + d_prime)`
  - Time discretization: `t_i = (sigma_max^(1/rho) + i/(N-1) * (sigma_min^(1/rho) - sigma_max^(1/rho)))^rho`, rounded by `net.round_sigma`, followed by `t_N = 0`
- Mapping to repo: [samplers/euler.py](/home/wjy/scifi/autoresearch-sampler/samplers/euler.py), [samplers/heun.py](/home/wjy/scifi/autoresearch-sampler/samplers/heun.py), and [model_adapter.py](/home/wjy/scifi/autoresearch-sampler/model_adapter.py).
- Upstream verification target: local clone `third_party/upstream-edm` at commit `008a4e5316c8e3bfe61a62f874bddba254295afb`.
- Deviations: stochastic churn is frozen off (`S_churn=0`, `S_noise=1`), matching the deterministic ODE path used for benchmarking.
