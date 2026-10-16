"""Perfiles de capacidades independientes de los adaptadores visuales."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StealthConfig:
    vision_range: float = 245
    vision_angle: float = 75
    detection_time: float = 0.25
    patrol_speed: float = 48
    chase_speed: float = 110
    search_duration: float = 15
    confusion_duration: float = 1
    search_end_duration: float = 1
    surprise_duration: float = 0.32
    assisted_tracking: bool = True
