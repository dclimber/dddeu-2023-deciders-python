from typing import Type

import deciders


class InMemoryDecider:

    def __init__(self, decider: Type[deciders.Decider]) -> None:
        self.decider = decider
        self.state: deciders.State = self.decider.initial_state()

    def decide(self, command: deciders.Command) -> list[deciders.Event]:
        events = self.decider.decide(command, self.state)
        for event in events:
            self.state = self.decider.evolve(self.state, event)
        return events
