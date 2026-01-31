from dataclasses import dataclass
import time
import numpy as np

@dataclass
class Frame:
    image: np.ndarray
    timestamp: float

    @classmethod
    def now(cls, image: np.ndarray):
        return cls(image=image, timestamp=time.time())
