from typing import Type

import interfaces


class InMemoryDecider:

    def __init__(self, decider: Type[interfaces.Aggregate]) -> None:
        self.decider = decider
        self.state: interfaces.State = self.decider.initial_state()

    def decide(self, command: interfaces.Command) -> list[interfaces.Event]:
        events = self.decider.decide(command, self.state)
        for event in events:
            self.state = self.decider.evolve(self.state, event)
        return events
