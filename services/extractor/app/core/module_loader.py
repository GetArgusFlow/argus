# argus/services/extractor/app/core/module_loader.py

from typing import Dict, Any
from loguru import logger
import importlib
import pkgutil


def discover_and_load_modules(package_path: str) -> Dict[str, Any]:
    """
    Scans a package path, dynamically discovers all submodules,
    and loads them.
    """
    loaded_modules = {}

    try:
        # Import the main package (e.g., app.modules.fields)
        package = importlib.import_module(package_path)
    except ImportError as e:
        logger.error(f"Could not import main package at '{package_path}': {e}")
        return {}

    # Use pkgutil to find all modules in the package directory
    for module_info in pkgutil.iter_modules(package.__path__, package_path + "."):
        module_name = module_info.name.split(".")[-1]

        # We are interested in the 'extract' submodule of each module
        full_extract_path = f"{module_info.name}.extract"

        try:
            module = importlib.import_module(full_extract_path)

            if hasattr(module, "extract") and callable(getattr(module, "extract")):
                loaded_modules[module_name] = module
                logger.debug(
                    f"Module '{module_name}' from '{package_path}' successfully loaded."
                )
            else:
                logger.warning(
                    f"Module '{full_extract_path}' has no 'extract' function. Skipping."
                )

        except ImportError:
            # This is normal if a module doesn't have an 'extract.py', so log at a lower level
            logger.trace(f"No 'extract.py' found for module '{module_name}'. Skipping.")
        except Exception as e:
            logger.error(
                f"Error loading module '{full_extract_path}': {e}", exc_info=True
            )

    return loaded_modules
