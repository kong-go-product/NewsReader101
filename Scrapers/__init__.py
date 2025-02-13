import os
import importlib

# Automatically import all modules in the `scrapers` directory
__all__ = []  # List to hold imported modules/functions

scraper_dir = os.path.dirname(__file__)
for filename in os.listdir(scraper_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        module = importlib.import_module(f"Scrapers.{module_name}")
        __all__.append(module_name)
        globals()[module_name] = module 
