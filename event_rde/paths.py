from typing import Optional

import jax
import jax.numpy as jnp
import jax.tree_util as jtu
from diffrax import AbstractPath
from jaxtyping import Array, Real


class SpikeTrain(AbstractPath):
    t0: Real
    t1: Real
    num_spikes: int
    spike_times: Array
    spike_cumsum: Array
    num_neurons: int

    def __init__(self, t0, t1, spike_times, spike_mask):
        self.t0 = t0
        self.t1 = t1
        self.num_spikes = spike_times.shape[0]
        self.spike_times = jnp.insert(spike_times, 0, t0)
        self.spike_cumsum = jnp.array(
            jtu.tree_map(lambda x: jnp.cumsum(jnp.insert(x, 0, jnp.array(False))), spike_mask),
            dtype=float,
        )
        self.num_neurons = self.spike_cumsum.shape[0]

    def evaluate(self, t0: Real, t1: Optional[Real] = None, left: Optional[bool] = True) -> Array:
        del left
        if t1 is not None:
            return self.evaluate(t1 - t0)
        idx = jnp.searchsorted(self.spike_times, t0)
        idx = jnp.where(idx > 0, idx - 1, idx)
        out = jax.lax.dynamic_slice(self.spike_cumsum, (0, idx), (self.num_neurons, 1))[:, 0]
        return out
