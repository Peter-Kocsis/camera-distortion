"""
Module for hadnlind JSON files
"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

from datetime import date
import numpy as np


def serialize(obj):
    """
    JSON serializer for objects not serializable by default json code
    :param obj: The object to be serailized
    :returns: The serailized object
    """

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
