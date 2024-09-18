import abc
from typing import List


# Define a custom metaclass that enforces the presence of type aliases
class DeciderMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Check for required TypeAliases
        required_aliases = ["State", "Command", "Event"]
        for alias in required_aliases:
            if not hasattr(cls, alias):
                raise TypeError(f"Class {name} must define a type alias for '{alias}'")

        return cls


class DeciderAggregate(metaclass=DeciderMeta):
    # TODO: Differentiate between input and ouput states
    class Event(abc.ABC):
        pass

    class State(abc.ABC):

        @abc.abstractmethod
        def evolve(self, event: "DeciderAggregate.Event") -> "DeciderAggregate.State":
            raise NotImplementedError()

    class Command(abc.ABC):
        @abc.abstractmethod
        def decide(
            self, state: "DeciderAggregate.State"
        ) -> List["DeciderAggregate.Event"]:
            raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def initial_state(cls) -> State:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def is_terminal(cls, state: State) -> bool:
        raise NotImplementedError()

    @classmethod
    def decide(cls, command: Command, state: State) -> List[Event]:
        return command.decide(state)

    @classmethod
    def evolve(cls, state: State, event: Event) -> State:
        return state.evolve(event)


class Decider(abc.ABC):
    @abc.abstractmethod
    def decide(
        self, command: DeciderAggregate.Command, state: DeciderAggregate.State
    ) -> List[DeciderAggregate.Event]:
        raise NotImplementedError()
