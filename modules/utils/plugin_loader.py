# modules/utils/plugin_loader.py
import os
import pkgutil
import importlib
import modules.scanners as scanners
import modules.utils as utils

def sync_plugins(data_manager):
    """
    Scans for scanners and list-UI modules, then updates info.json.
    (English comment for contributors)
    """
    # 1. Discover Package Managers
    scanner_modules = [name for _, name, _ in pkgutil.iter_modules(scanners.__path__)]
    managers = []
    for m in scanner_modules:
        if m.endswith('_list_scanner'):
            manager_name = m.replace('_list_scanner', '')
            managers.append(manager_name)
    
    # Update data_manager's internal list (added a new key 'available_managers')
    data_manager.data["status"]["available_managers"] = managers
    
    # 2. Discover UI Methods
    ui_modules = [name for _, name, _ in pkgutil.iter_modules(utils.__path__) if name.startswith('list_')]
    data_manager.data["status"]["available_uis"] = ui_modules
    
    data_manager.save()
    return managers, ui_modules

def load_module(package_path):
    """Dynamically imports a module by string path."""
    return importlib.import_module(package_path)
