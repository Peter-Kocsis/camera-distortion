import numpy as np
from datetime import date


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = serialize(value)
        return obj

    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, np.ndarray):
        serial = obj.tolist()
        return serial

    if hasattr(obj, "__dict__"):
        return serialize(obj.__dict__)

    return obj
