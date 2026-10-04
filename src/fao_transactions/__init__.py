"""Geneva Property Transactions Pipeline package."""

import sys

# Prevent incompatible external Python 3.13 user site-packages from polluting the 3.12 virtualenv
sys.path = [p for p in sys.path if "Python313" not in p and "Python311" not in p]

__version__ = "0.1.0"

