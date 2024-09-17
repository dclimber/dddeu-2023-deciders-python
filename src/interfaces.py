import abc


class Event(abc.ABC):
    pass


class State(abc.ABC):
    pass

    @abc.abstractmethod
    def evolve(self, event: Event) -> "State":
        pass


class Command(abc.ABC):
    @abc.abstractmethod
    def decide(self, state: State) -> list[Event]:
        pass


class Policy(abc.ABC):
    @abc.abstractmethod
    def react(self, event: Event) -> list[Command]:
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
