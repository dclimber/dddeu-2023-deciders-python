import abc


class Event(abc.ABC):
    pass


class State(abc.ABC):

    @abc.abstractmethod
    def evolve(self, event: Event) -> "State":
        raise NotImplementedError()


class Command(abc.ABC):
    @abc.abstractmethod
    def decide(self, state: State) -> list[Event]:
        raise NotImplementedError()


class DeciderAggregate(abc.ABC):
    # TODO: Differentiate between input and ouput states

    @classmethod
    @abc.abstractmethod
    def initial_state(cls) -> State:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def is_terminal(cls, state: State) -> bool:
        raise NotImplementedError()

    @classmethod
    def decide(cls, command: Command, state: State) -> list[Event]:
        return command.decide(state)

    @classmethod
    def evolve(cls, state: State, event: Event) -> State:
        return state.evolve(event)


class Decider(abc.ABC):
    @abc.abstractmethod
    def decide(self, command: Command, state: State) -> list[Event]:
        raise NotImplementedError()
