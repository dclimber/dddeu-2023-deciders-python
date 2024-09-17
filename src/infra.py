from typing import Type

import interfaces


class InMemoryDecider:

    def __init__(self, decider: Type[interfaces.Decider]) -> None:
        self.decider = decider
        self.state: interfaces.State = self.decider.initial_state()

    def decide(self, command: interfaces.Command) -> list[interfaces.Event]:
        events = self.decider.decide(command, self.state)
        self.state = self.fold(self.state, events)
        return events

    def fold(
        self, start_state: interfaces.State, events: list[interfaces.Event]
    ) -> interfaces.State:
        state = start_state
        for event in events:
            state = self.decider.evolve(state, event)
        return state
