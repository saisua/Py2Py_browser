from typing import Any
from dataclasses import dataclass, field
from datetime import datetime

from communication.concurrency_layers import concurrency_layer_t


@dataclass(slots=True)
class Message:
    objective: int
    priority: int
    topic: int
    content: Any
    layer: concurrency_layer_t
    timestamp: datetime = field(default_factory=datetime.now)

    def __gt__(self, other: 'Message'):
        return (
            self.priority > other.priority or
            self.timestamp < other.timestamp
        )

    def __lt__(self, other: 'Message'):
        return (
            self.priority < other.priority or
            self.timestamp > other.timestamp
        )

    def __eq__(self, other: 'Message'):
        return (
            self.priority == other.priority and
            self.timestamp == other.timestamp
        )
