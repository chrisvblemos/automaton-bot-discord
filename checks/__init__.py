import os
import importlib

module_dir = os.path.dirname(__file__)
for filename in os.listdir(module_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)