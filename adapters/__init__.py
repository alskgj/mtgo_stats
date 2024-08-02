"""

    adapters
    ========

Adapters contains base classes and concrete implementations of code interfacing with the real world.
DB access or API clients are here.
"""

from .mtgo import MtgoAPI
from .mtgo import MtgoClient
from .mtgo import api
