"""
======
Sensor
======

Author: Reuven Mol

Inertial sensor simulation module.

This module implements a stochastic inertial sensor model including:
- bias instability (random walk)
- scale factor error
- additive noise
- fixed bias
- misalignment

It is intended as a building block for IMU / gyro / accelerometer simulation.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray


Array = NDArray[np.float64]


@dataclass(frozen=True)
class SensorModel:
    """
    Static configuration for a sensor.

    Parameters
    ----------
    output_data_rate_hz : float
        Sampling rate of the sensor in Hz.

    bias : ndarray
        Constant deterministic bias (same shape as measurement vector).

    scale_factor_ppm : float
        Scale factor error in parts per million.

    noise_density : float
        White noise density [unit / sqrt(Hz)].

    bias_instability : float
        Random-walk strength of bias (per sqrt(second)).

    misalignment : ndarray, optional
        3x3 rotation matrix representing sensor frame misalignment.

    full_scale : float, optional
        Full-scale range of sensor (for saturation modeling later).

    quantization_step : float, optional
        ADC quantization step size.

    measure_units : str
        Physical units of measurement (e.g. "rad/s", "m/s^2").
    """

    output_data_rate_hz: float
    bias: Array
    scale_factor_ppm: float
    noise_density: float
    bias_instability: float

    misalignment: Optional[Array] = None
    full_scale: Optional[float] = None
    quantization_step: Optional[float] = None

    measure_units: str = ""


class Sensor:
    """
    Stochastic inertial sensor simulator.

    This class models a discrete-time sensor with:
    - bias drift (random walk)
    - scale factor error
    - misalignment
    - additive white noise

    Notes
    -----
    This is NOT a full navigation-grade IMU model yet.
    Future extensions should include:
    - Gauss-Markov bias model (instead of random walk)
    - bandwidth-limited noise (1st order filter)
    - temperature-dependent error terms
    """

    def __init__(self, model: SensorModel, seed: Optional[int] = None):
        self.model = model

        # Time-varying stochastic bias (same shape as measurement vector)
        self.current_bias: Array = np.zeros_like(model.bias)

        # Random number generator (make simulation reproducible)
        self.rng = np.random.default_rng(seed)

        # Reserved for future extensions (e.g. filtering, internal dynamics)
        self.internal_state = None

    def measure(self, truth: Array, duration: float) -> Array:
        """
        Simulate sensor measurements over a time interval.

        Parameters
        ----------
        truth : ndarray
            True input signal (e.g. angular rate or acceleration).
            Shape: (3,) or (N,)

        duration : float
            Simulation duration in seconds.

        Returns
        -------
        ndarray
            Simulated sensor output over time.
            Shape: (N_samples, truth_shape)

        Notes
        -----
        - Assumes constant truth over duration (zero-order hold)
        - Uses fixed sampling rate from sensor model
        """

        truth = np.asarray(truth)

        # rotate into sensor frame
        aligned_truth = self.misalignment(truth)

        dt = 1.0 / self.model.output_data_rate_hz
        n_samples = int(duration * self.model.output_data_rate_hz)

        signal: list[Array] = []

        for _ in range(n_samples):
            self.update_bias(dt)

            x = self.scale(aligned_truth)
            x = self.add_bias(x)
            x = self.add_noise(x)

            signal.append(x)

        return np.asarray(signal)

    def update_bias(self, dt: float) -> None:
        """
        Random-walk bias update.

        Recommendation
        --------------
        Replace with Gauss-Markov process for more realistic IMU modeling:
        b(t+dt) = exp(-dt/tau)*b(t) + noise
        """

        self.current_bias += (
            self.model.bias_instability
            * np.sqrt(dt)
            * self.rng.normal(size=self.current_bias.shape)
        )

    def misalignment(self, truth: Array) -> Array:
        """
        Apply sensor frame misalignment.

        Recommendation
        --------------
        Ensure misalignment is a proper 3x3 rotation matrix.
        """

        if self.model.misalignment is not None:
            return self.model.misalignment @ truth
        return truth

    def scale(self, truth: Array) -> Array:
        """
        Apply scale factor error.

        Recommendation
        --------------
        Upgrade to per-axis scale matrix for realistic IMUs.
        """

        scale = 1.0 + self.model.scale_factor_ppm / 1_000_000.0
        return scale * truth

    def add_bias(self, truth: Array) -> Array:
        """
        Add deterministic + stochastic bias components.
        """

        return truth + self.model.bias + self.current_bias

    def add_noise(self, truth: Array) -> Array:
        """
        Add white Gaussian noise.

        Recommendation
        --------------
        Current model assumes white noise only.
        Real IMUs require bandwidth-limited noise shaping.
        """

        sigma = self.model.noise_density * np.sqrt(self.model.output_data_rate_hz)
        noise = self.rng.normal(scale=sigma, size=truth.shape)
        return truth + noise