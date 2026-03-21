import os

if os.environ.get("KND_DEBUG_INIT") == "1":
    print("KND INIT LOADED FROM:", __file__)
    print("FILES IN FOLDER:", os.listdir(os.path.dirname(__file__)))

from .world import KNDWorld

__all__ = ["KNDWorld"]
