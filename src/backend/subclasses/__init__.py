import os
import importlib
import inspect

# Get the directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get all Python files in the directory
python_files = [f[:-3] for f in os.listdir(current_dir) 
                if f.endswith('.py') and f != '__init__.py']

# Dictionary to store all classes
__all__ = []

# Import all classes from each file
for module_name in python_files:
    # Import the module
    module = importlib.import_module(f'.{module_name}', package=__package__)
    
    # Get all classes from the module
    classes = inspect.getmembers(module, inspect.isclass)
    
    # Add classes to the current namespace
    for name, cls in classes:
        if cls.__module__.startswith(__package__):
            globals()[name] = cls
            __all__.append(name)