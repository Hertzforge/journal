"""Writes data/response.csv: the invented response this sample plots.

The system is made up. It has two modes; its driving-point accelerance is their modal sum. Two
noisy "estimates" of its magnitude are made by multiplying the reference by log-normal noise
whose spread falls with the square root of the number of averages. The noise comes from a fixed
seed, so this file writes the same data every time.

    python code/make_data.py        (run from the article folder)

Standard library only. MIT license.
"""

import csv
import math
import random

# The invented system: natural frequency (Hz), damping ratio, modal constant (1/kg).
MODES = [
    (120.0, 0.020, 1.0),
    (310.0, 0.015, 0.6),
]
SEED = 20261114
SPREAD_AT_8_AVERAGES = 0.20


def accelerance(frequency_hz: float) -> float:
    """The magnitude of the driving-point accelerance, in (m/s^2)/N."""
    omega = 2 * math.pi * frequency_hz
    total = 0j
    for natural_hz, damping, constant in MODES:
        omega_r = 2 * math.pi * natural_hz
        total += -(omega ** 2) * constant / complex(omega_r ** 2 - omega ** 2, 2 * damping * omega_r * omega)
    return abs(total)


def main() -> None:
    noise = random.Random(SEED)
    with open('data/response.csv', 'w', newline='') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['frequency_hz', 'reference', 'estimate_8_averages', 'estimate_64_averages'])
        for step in range(241):
            frequency = 20.0 + 2.0 * step
            reference = accelerance(frequency)
            rough = reference * math.exp(noise.gauss(0.0, SPREAD_AT_8_AVERAGES))
            fine = reference * math.exp(noise.gauss(0.0, SPREAD_AT_8_AVERAGES / math.sqrt(64 / 8)))
            writer.writerow([f'{frequency:.0f}', f'{reference:.6g}', f'{rough:.6g}', f'{fine:.6g}'])


if __name__ == '__main__':
    main()
