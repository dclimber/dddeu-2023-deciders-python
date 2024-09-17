import dataclasses

from interfaces import Command, Decider, Event, State


# ---- Implementations ----
class Cat(Decider):

    # -- Methods --
    @classmethod
    def initial_state(cls) -> State:
        return cls.AwakeState()

    @classmethod
    def is_terminal(cls, state: State) -> bool:
        return False

    # -- Commands --
    class WakeUpCommand(Command):

        def decide(self, state: State) -> list[Event]:
            if isinstance(state, Cat.AsleepState):
                return [Cat.WokeUpEvent()]
            return []

    class GoToSleepCommand(Command):
        def decide(self, state: State) -> list[Event]:
            if isinstance(state, Cat.AwakeState):
                return [Cat.GotToSleepEvent()]
            return []

    # -- Events --
    @dataclasses.dataclass(frozen=True)
    class WokeUpEvent(Event):
        sound: str = "meow"

    @dataclasses.dataclass(frozen=True)
    class GotToSleepEvent(Event):
        sound: str = "purr"

    # -- States --
    @dataclasses.dataclass(frozen=True)
    class AsleepState(State):
        sound: str = "meow"

        def evolve(self, event: Event) -> State:
            if isinstance(event, Cat.WokeUpEvent):
                return Cat.AwakeState()
            raise Exception(f"Unknown event `{event}`")

    @dataclasses.dataclass(frozen=True)
    class AwakeState(State):
        sound: str = "purr"

        def evolve(self, event: Event) -> State:
            if isinstance(event, Cat.GotToSleepEvent):
                return Cat.AsleepState()
            raise Exception(f"Unknown event `{event}`")
