"""This library provides a set of tools for listening tests. Including:
- basic audio processing, such as normalization, convolution, etc.
- stimuli and combinations preparation
- GUI classes (examples) for basic listening tests (ABX, Adaptive, more in the future)
"""

from .audiotools import audio_stats
from .processing import (
    straight,
    gain_adjustment,
    convolution,
    match_fs,
    audio_stats_logging,
    )
from .stimuli import play_sound