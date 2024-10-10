import dataclasses
from typing import List, Literal

from interfaces import DeciderAggregate


# ---- Implementations ----
class Bulb(DeciderAggregate):

    class Event(DeciderAggregate.Event):
        pass

    class Command(DeciderAggregate.Command):
        pass

    class State(DeciderAggregate.State):
        pass

    # -- Methods --
    @classmethod
    def initial_state(cls) -> "Bulb.State":
        return cls.NotFittedState()

    @classmethod
    def is_terminal(cls, state: "Bulb.State") -> bool:
        match state:
            case cls.BlownState(): return True
            case _: return False

    # -- Commands --
    @dataclasses.dataclass(frozen=True)
    class FitCommand(Command):
        max_uses: int

        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            match state:
                case Bulb.NotFittedState():
                    return [Bulb.FittedEvent(self.max_uses)]
                case _: return []

    class SwitchOnCommand(Command):
        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            match state:
                case Bulb.WorkingState(status = "Off", remaining_uses = 0):
                    return [Bulb.BlewEvent()]
                case Bulb.WorkingState(status = "Off"):
                    return [Bulb.SwitchedOnEvent()]
                case _: return []

    class SwitchOffCommand(Command):
        def decide(self, state: "Bulb.State") -> List["Bulb.Event"]:
            match state:
                case Bulb.WorkingState(status = "On"):
                    return [Bulb.SwitchedOffEvent()]
                case _: return []

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
            match event:
                case Bulb.FittedEvent():
                    return Bulb.WorkingState("Off", event.max_uses)
                case _:
                    raise Exception(f"Unknown event `{event}`")

    @dataclasses.dataclass(frozen=True)
    class WorkingState(State):
        status: Literal["On", "Off"]
        remaining_uses: int

        def evolve(self, event: "Bulb.Event") -> "Bulb.State":
            match event:
                case Bulb.SwitchedOnEvent():
                    return Bulb.WorkingState("On", self.remaining_uses - 1)
                case Bulb.SwitchedOffEvent():
                    return Bulb.WorkingState("Off", self.remaining_uses)
                case Bulb.BlewEvent():
                    return Bulb.BlownState()
                case _:
                    raise Exception(f"Unknown event `{event}`")

    class BlownState(State):
        def evolve(self, _: "Bulb.Event") -> "Bulb.State":
            return self
