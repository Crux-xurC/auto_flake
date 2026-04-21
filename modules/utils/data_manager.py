# modules/utils/data_manager.py
import json
import os

class DataManager:
    """
    Manages the centralized JSON database (info/project_data.json).
    This class ensures all modules share the same state and data.
    """
    
    def __init__(self, data_path="info/project_data.json"):
        self.data_path = data_path
        self.data = self._load_data()

    def _load_data(self):
        """Initializes data if file doesn't exist, otherwise loads it."""
        if not os.path.exists(self.data_path):
            return {
                "status": {
                    "is_initialized": False,
                    "current_phase": "idle"
                },
                "selection": {
                    "manager": None,
                    "raw_list": []
                },
                "dictionary": []
            }
        
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Fallback for corrupted files
            return {"status": {"is_initialized": False}, "selection": {}, "dictionary": []}

    def save(self):
        """Persists the current state to the JSON file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def update_phase(self, phase_name):
        """Updates the application's current progress phase."""
        self.data["status"]["current_phase"] = phase_name
        self.data["status"]["is_initialized"] = True
        self.save()

    def add_to_dictionary(self, app_data):
        """
        Appends analyzed application data to the dictionary list.
        app_data should follow the schema: {name, source, depends, package_name}
        """
        self.data["dictionary"].append(app_data)
        self.save()
