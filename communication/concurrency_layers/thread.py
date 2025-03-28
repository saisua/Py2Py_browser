from dataclasses import dataclass


@dataclass(slots=True)
class ThreadLayer:
    id: int

    def must_lock(self, other_layer):
        if isinstance(other_layer, ThreadLayer) and self.id == other_layer.id:
            return False
        return True
