from typing import Dict


class Filter(object):
    """Filter a set of values for inclusion within intervals specified by extents."""
    def __init__(self, values: Dict, extents: Dict):
        self.values = values
        self.extents = extents

    def filter(self):
        """Perform the filtering."""
        filtered_values = None
        if "end" in self.extents.keys() and "values" in self.values.keys():
            vals = self.values["values"]
            start_ind = vals.index(self.extents["start"])
            end_ind = vals.index(self.extents["end"])
            filtered_values = vals[start_ind:end_ind+1]
        return filtered_values