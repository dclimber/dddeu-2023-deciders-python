import dataclasses
import uuid
from typing import Callable, Type

import interfaces
from deciders import bulb, cat


class InMemoryDecider(interfaces.Decider):

    def __init__(self, aggregate: Type[interfaces.Aggregate]) -> None:
        self.aggregate = aggregate
        self.state: interfaces.State = self.aggregate.initial_state()

    def decide(self, command: interfaces.Command) -> list[interfaces.Event]:
        events = self.aggregate.decide(command, self.state)
        for event in events:
            self.state = self.aggregate.evolve(self.state, event)
        return events


def cat_serializer(state: interfaces.State) -> str:
    if isinstance(state, cat.Cat.AsleepState):
        return "asleep"
    if isinstance(state, cat.Cat.AwakeState):
        return "awake"
    raise Exception(f"Unknown state: {state}")


def cat_deserializer(text: str) -> interfaces.State:
    if text == "asleep":
        return cat.Cat.AsleepState()
    if text == "awake":
        return cat.Cat.AwakeState()
    raise Exception(f"Unknown state: {text}")


def bulb_serializer(state: interfaces.State) -> str:
    if isinstance(state, bulb.Bulb.NotFittedState):
        return "not_fitted"
    if isinstance(state, bulb.Bulb.WorkingState):
        return f"working:{state.status}:{state.remaining_uses}"
    if isinstance(state, bulb.Bulb.BlownState):
        return "blown"
    raise Exception(f"Unknown state: {state}")


def bulb_deserializer(text: str) -> interfaces.State:
    if text == "not_fitted":
        return bulb.Bulb.NotFittedState()
    if text.startswith("working:"):
        parts = text.split(":")
        return bulb.Bulb.WorkingState(parts[1], int(parts[2]))
    if text == "blown":
        return bulb.Bulb.BlownState()
    raise Exception(f"Unknown state: {text}")


class StateBasedDecider(interfaces.Decider):
    @dataclasses.dataclass(frozen=True)
    class StoredValue:
        state: str
        etag: uuid.UUID

    def __init__(
        self,
        aggregate: Type[interfaces.Aggregate],
        serializer: Callable[[interfaces.State], str],
        deserializer: Callable[[str], interfaces.State],
        container: dict[str, StoredValue],
        key: str,
    ) -> None:
        self.aggregate = aggregate
        self.container: dict[str, StateBasedDecider.StoredValue] = container
        self.serializer = serializer
        self.deserializer = deserializer
        self.key = key

    def decide(self, command: interfaces.Command) -> list[interfaces.Event]:
        stored_value: StateBasedDecider.StoredValue | None = self.container.get(
            self.key
        )
        if stored_value is None:
            state = self.aggregate.initial_state()
            etag = uuid.uuid4()
        else:
            state = self.deserializer(stored_value.state)
            etag = stored_value.etag
        events = self.aggregate.decide(command, state)
        for event in events:
            state = self.aggregate.evolve(state, event)
        self.__store(state, etag)
        return events

    @property
    def state(self) -> interfaces.State:
        return self.deserializer(self.container[self.key].state)

    def __store(self, state: interfaces.State, etag: uuid.UUID) -> None:
        if self.key in self.container and self.container[self.key].etag != etag:
            raise ValueError("ETag mismatch")
        self.container[self.key] = StateBasedDecider.StoredValue(
            state=self.serializer(state), etag=etag
        )
