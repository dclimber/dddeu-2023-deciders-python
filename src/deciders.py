import abc
import dataclasses
from typing import Literal


# ---- interfaces ----
class Command(abc.ABC):
    pass


class Event(abc.ABC):
    pass


class State(abc.ABC):
    pass


class Decider(abc.ABC):
    # TODO: Differentiate between input and ouput states

    @classmethod
    @abc.abstractmethod
    def decide(cls, command: Command, state: State) -> list[Event]:
        pass

    @classmethod
    @abc.abstractmethod
    def evolve(cls, state: State, event: Event) -> State:
        pass

    @classmethod
    @abc.abstractmethod
    def initial_state(cls) -> State:
        pass

    @classmethod
    @abc.abstractmethod
    def is_terminal(cls, state: State) -> bool:
        pass


# ---- Implementations ----
class Bulb(Decider):
    # -- Interfaces --
    class BulbCommand(Command):
        pass

    class BulbState(State):
        pass

    class BulbEvent(Event):
        pass

    # -- Commands --
    @dataclasses.dataclass(frozen=True)
    class FitCommand(BulbCommand):
        max_uses: int

    @dataclasses.dataclass(frozen=True)
    class SwitchOnCommand(BulbCommand):
        pass

    @dataclasses.dataclass(frozen=True)
    class SwitchOffCommand(BulbCommand):
        pass

    # -- Events --
    @dataclasses.dataclass(frozen=True)
    class FittedEvent(BulbEvent):
        max_uses: int

    @dataclasses.dataclass(frozen=True)
    class SwitchedOnEvent(BulbEvent):
        pass

    @dataclasses.dataclass(frozen=True)
    class SwitchedOffEvent(BulbEvent):
        pass

    @dataclasses.dataclass(frozen=True)
    class BlewEvent(BulbEvent):
        pass

    # -- States --
    class NotFittedState(BulbState):
        pass

    @dataclasses.dataclass(frozen=True)
    class WorkingState(BulbState):
        status: Literal["On", "Off"]
        remaining_uses: int

    class Blown(BulbState):
        pass

    class BlownState(BulbState):
        pass

    # -- Methods --
    @classmethod
    def decide(cls, command: Command, state: State) -> list[Event]:
        if isinstance(command, cls.FitCommand) and isinstance(
            state, cls.NotFittedState
        ):
            return [cls.FittedEvent(command.max_uses)]
        if isinstance(command, cls.SwitchOnCommand) and isinstance(
            state, cls.WorkingState
        ):
            if state.status == "On":
                return []
            return [cls.SwitchedOnEvent()]
        if isinstance(command, cls.SwitchOffCommand) and isinstance(
            state, cls.WorkingState
        ):
            if state.status == "Off":
                return []
            return [cls.SwitchedOffEvent()]
        if isinstance(command, cls.SwitchOnCommand) and isinstance(
            state, cls.BlownState
        ):
            return []
        if isinstance(command, cls.SwitchOffCommand) and isinstance(
            state, cls.BlownState
        ):
            return []
        raise Exception(f"Unknown command `{command}` or state `{state}`")

    @classmethod
    def evolve(cls, state: State, event: Event) -> State:
        if isinstance(state, cls.NotFittedState) and isinstance(event, cls.FittedEvent):
            return cls.WorkingState("Off", remaining_uses=event.max_uses)
        if isinstance(state, cls.WorkingState) and isinstance(
            event, cls.SwitchedOnEvent
        ):
            if state.remaining_uses > 0:
                return cls.WorkingState("On", state.remaining_uses - 1)
            return cls.BlownState()
        if isinstance(state, cls.WorkingState) and isinstance(
            event, cls.SwitchedOffEvent
        ):
            if state.remaining_uses > 0:
                return cls.WorkingState("Off", state.remaining_uses - 1)
            return cls.BlownState()
        if isinstance(state, cls.BlownState) and isinstance(event, cls.BlewEvent):
            return cls.BlownState()
        raise Exception(
            f"Unknown state `{state} {type(state)}` or event `{event} {type(event)}`"
        )

    @classmethod
    def initial_state(cls) -> State:
        return cls.NotFittedState()

    @classmethod
    def is_terminal(cls, state: State) -> bool:
        if isinstance(state, cls.BlownState):
            return True
        return False
