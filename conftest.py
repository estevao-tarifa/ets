import sys
import os

# Add project root so 'backend.*' imports resolve
_root = os.path.dirname(__file__)
if _root not in sys.path:
    sys.path.insert(0, _root)
# Legacy: also add backend/ so bare 'domain.*' imports still work in unit tests
_backend = os.path.join(_root, "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)
