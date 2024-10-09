from typing import List, TypeAlias, Union

import interfaces


def compose_decider_aggregates(
    decider_x: interfaces.DeciderAggregate,
    decider_y: interfaces.DeciderAggregate,
) -> interfaces.DeciderAggregate:
    class ComposedDecider(interfaces.DeciderAggregate):

        CommandX: TypeAlias = decider_x.Command
        EventX: TypeAlias = decider_x.Event
        StateX: TypeAlias = decider_x.State
        CommandY: TypeAlias = decider_y.Command
        EventY: TypeAlias = decider_y.Event
        StateY: TypeAlias = decider_y.State

        class CombinedState(interfaces.DeciderAggregate.State):
            def __init__(
                self,
                x_state: "ComposedDecider.StateX",
                y_state: "ComposedDecider.StateY",
            ) -> None:
                self.decider_x_state = x_state
                self.decider_y_state = y_state

            def __str__(self) -> str:
                return (
                    f"{self.__class__.__name__}({decider_x.__class__.__name__}"
                    f", {decider_y.__class__.__name__})"
                )

            def __repr__(self) -> str:
                return str(self)

            def evolve(
                self, event: Union["ComposedDecider.EventX", "ComposedDecider.EventY"]
            ) -> Union["ComposedDecider.StateX", "ComposedDecider.StateY"]:
                if isinstance(event, ComposedDecider.EventX):
                    state_x = decider_x.initial_state()
                    return state_x.evolve(event)
                elif isinstance(event, ComposedDecider.EventY):
                    state_y = decider_y.initial_state()
                    return state_y.evolve(event)
                raise ValueError(f"Invalid event {event}")

        def __str__(self) -> str:
            return f"{self.__class__.__name__}({decider_x}, {decider_y})"

        def __repr__(self) -> str:
            return str(self)

        @classmethod
        def decide(
            cls,
            command: CommandX | CommandY,
            state: StateX | StateY | CombinedState,
        ) -> List["EventX"] | List["EventY"]:
            if isinstance(command, decider_x.Command) and (
                isinstance(state, decider_x.State)
                or isinstance(state, ComposedDecider.CombinedState)
            ):
                if isinstance(state, ComposedDecider.CombinedState):
                    x_state = state.decider_x_state
                else:
                    x_state = state
                return decider_x.decide(command, x_state)
            elif isinstance(command, ComposedDecider.CommandY) and (
                isinstance(state, ComposedDecider.StateY)
                or isinstance(state, ComposedDecider.CombinedState)
            ):
                if isinstance(state, ComposedDecider.CombinedState):
                    y_state = state.decider_y_state
                else:
                    y_state = state
                return decider_y.decide(command, y_state)
            raise ValueError(f"Invalid command {command} or state {state}")

        @classmethod
        def evolve(
            cls,
            state: StateX | StateY | CombinedState,
            event: EventX | EventY,
        ) -> StateX | StateY:
            if isinstance(event, ComposedDecider.EventX) and (
                isinstance(state, ComposedDecider.StateX)
                or isinstance(state, ComposedDecider.CombinedState)
            ):
                if isinstance(state, ComposedDecider.CombinedState):
                    x_state = state.decider_x_state
                else:
                    x_state = state
                return decider_x.evolve(x_state, event)
            elif isinstance(event, ComposedDecider.EventY) and (
                isinstance(state, ComposedDecider.StateY)
                or isinstance(state, ComposedDecider.CombinedState)
            ):
                if isinstance(state, ComposedDecider.CombinedState):
                    y_state = state.decider_y_state
                else:
                    y_state = state
                return decider_y.evolve(y_state, event)
            raise ValueError(f"Invalid event {event} or state {state}")

        @classmethod
        def initial_state(cls) -> interfaces.DeciderAggregate.State:
            return ComposedDecider.CombinedState(
                decider_x.initial_state(), decider_y.initial_state()
            )

        @classmethod
        def is_terminal(cls, state: StateX | StateY) -> bool:
            if isinstance(state, ComposedDecider.StateX):
                return decider_x.is_terminal(state)
            elif isinstance(state, ComposedDecider.StateY):
                return decider_y.is_terminal(state)
            raise ValueError(f"Invalid state {state}")

    return ComposedDecider()
