import customfpl.settings.base as stbase
import json
from pathlib import Path
import subprocess


class JsonData:
    """Class to save JSON data to some location

    This class cannot be instantiated by itself
    and read/write methods will only work
    when being called by the child class.
    """

    storage_root = stbase.JSON_ROOT

    def __init__(self):

        self.storage_file_path = None

    def __new__(cls, *args, **kwargs):
        if cls is JsonData:
            raise TypeError("json data may not be instantiated")
        return object.__new__(cls, *args, **kwargs)

    def read_json_data(self):
        if not self.storage_file_path:
            print("Raise exception")
            return None

        with open(self.storage_file_path, "r") as f:
            try:
                return json.loads(f.read())
            except:
                return None

    def write_json_data(self, data):
        if not self.storage_file_path:
            print("Raise Exception")
            return

        with open(self.storage_file_path, "w") as f:
            f.write(json.dumps(data))

    def delete_json_data(self):
        """Delete the JSON object that was expected to be returned

        This is done to refresh the server with new data
        """
        file_path = Path(self.storage_file_path)

        if file_path.exists():
            try:
                subprocess.call(["rm", self.storage_file_path])
            except:
                print("Some error")
