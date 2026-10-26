import sys
from importlib.metadata import version

print("Python         :", sys.version.split()[0])
print("Di dalam venv  :", sys.prefix != sys.base_prefix)
print("Lokasi prefix  :", sys.prefix)
print("FastAPI        :", version("fastapi"))
