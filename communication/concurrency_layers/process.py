from dataclasses import dataclass


@dataclass(slots=True)
class ProcessLayer:
    id: int

    def must_lock(self, other_layer):
        if isinstance(other_layer, ProcessLayer) and self.id == other_layer.id:
            return False
        return True
