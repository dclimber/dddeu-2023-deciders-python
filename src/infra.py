from typing import Type

import interfaces


class InMemoryDecider(interfaces.Decider):

    def __init__(self, aggregate: Type[interfaces.Aggregate]) -> None:
        self.aggregate = aggregate
        self.state: interfaces.State = self.aggregate.initial_state()

    def decide(self, command: interfaces.Command) -> list[interfaces.Event]:
        events = self.aggregate.decide(command, self.state)
        for event in events:
            self.state = self.aggregate.evolve(self.state, event)
        return events
