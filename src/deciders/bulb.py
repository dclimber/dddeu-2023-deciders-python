import dataclasses
from typing import List, Literal, TypeAlias

from interfaces import DeciderAggregate


# ---- Implementations ----
class Bulb(DeciderAggregate):

    Event: TypeAlias = DeciderAggregate.Event
    Command: TypeAlias = DeciderAggregate.Command
    State: TypeAlias = DeciderAggregate.State

    # -- Methods --
    @classmethod
    def initial_state(cls) -> "Bulb.State":
        return cls.NotFittedState()

    @classmethod
    def is_terminal(cls, state: "Bulb.State") -> bool:
        if isinstance(state, cls.BlownState):
            return True
        return False

    # -- Commands --
    @dataclasses.dataclass(frozen=True)
    class FitCommand(Command):
        max_uses: int

        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            if isinstance(state, Bulb.NotFittedState):
                return [Bulb.FittedEvent(self.max_uses)]
            return []

    class SwitchOnCommand(Command):
        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            if isinstance(state, Bulb.WorkingState) and state.status == "Off":
                if state.remaining_uses == 0:
                    return [Bulb.BlewEvent()]
                return [Bulb.SwitchedOnEvent()]
            return []

    class SwitchOffCommand(Command):
        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            if isinstance(state, Bulb.WorkingState) and state.status == "On":
                return [Bulb.SwitchedOffEvent()]
            return []

    # -- Events --
    @dataclasses.dataclass(frozen=True)
    class FittedEvent(Event):
        max_uses: int

    @dataclasses.dataclass(frozen=True)
    class SwitchedOnEvent(Event):
        pass

    @dataclasses.dataclass(frozen=True)
    class SwitchedOffEvent(Event):
        pass

    @dataclasses.dataclass(frozen=True)
    class BlewEvent(Event):
        pass

    # -- States --
    class NotFittedState(State):
        def evolve(self, event: "Bulb.Event") -> "Bulb.State":
            if isinstance(event, Bulb.FittedEvent):
                return Bulb.WorkingState("Off", event.max_uses)
            raise Exception(f"Unknown event `{event}`")

    @dataclasses.dataclass(frozen=True)
    class WorkingState(State):
        status: Literal["On", "Off"]
        remaining_uses: int

        def evolve(self, event: "Bulb.Event") -> "Bulb.State":
            if isinstance(event, Bulb.SwitchedOnEvent):
                return Bulb.WorkingState("On", self.remaining_uses - 1)
            if isinstance(event, Bulb.SwitchedOffEvent):
                return Bulb.WorkingState("Off", self.remaining_uses)
            if isinstance(event, Bulb.BlewEvent):
                return Bulb.BlownState()
            raise Exception(f"Unknown event `{event}`")

    class BlownState(State):
        def evolve(self, _: "Bulb.Event") -> "Bulb.State":
            return self
