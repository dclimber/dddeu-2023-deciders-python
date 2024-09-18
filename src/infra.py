import dataclasses
import uuid
from typing import Callable, Type

import interfaces


def fold(
    evolve_function: Callable[
        [interfaces.DeciderAggregate.State, interfaces.DeciderAggregate.Event],
        interfaces.DeciderAggregate.State,
    ],
    initial_state: interfaces.DeciderAggregate.State,
    events: list[interfaces.DeciderAggregate.Event],
) -> interfaces.DeciderAggregate.State:
    state = initial_state
    for event in events:
        state = evolve_function(state, event)
    return state


class InMemoryDecider(interfaces.Decider):

    def __init__(self, aggregate: Type[interfaces.DeciderAggregate]) -> None:
        self.aggregate = aggregate
        self.state: interfaces.DeciderAggregate.State = self.aggregate.initial_state()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.aggregate})"

    def decide(
        self, command: interfaces.DeciderAggregate.Command
    ) -> list[interfaces.DeciderAggregate.Event]:
        events = self.aggregate.decide(command, self.state)
        self.state = fold(self.aggregate.evolve, self.state, events)
        return events


class StateBasedDecider(interfaces.Decider):
    @dataclasses.dataclass(frozen=True)
    class StoredValue:
        state: str
        etag: uuid.UUID

    def __init__(
        self,
        aggregate: Type[interfaces.DeciderAggregate],
        serializer: Callable[[interfaces.DeciderAggregate.State], str],
        deserializer: Callable[[str], interfaces.DeciderAggregate.State],
        container: dict[str, StoredValue],
        key: str,
    ) -> None:
        self.aggregate = aggregate
        self.container: dict[str, StateBasedDecider.StoredValue] = container
        self.serializer = serializer
        self.deserializer = deserializer
        self.key = key

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.aggregate})"

    def decide(
        self, command: interfaces.DeciderAggregate.Command
    ) -> list[interfaces.DeciderAggregate.Event]:
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
        state = fold(self.aggregate.evolve, state, events)
        self.__store(state, etag)
        return events

    @property
    def state(self) -> interfaces.DeciderAggregate.State:
        return self.deserializer(self.container[self.key].state)

    def __store(
        self, state: interfaces.DeciderAggregate.State, etag: uuid.UUID
    ) -> None:
        if self.key in self.container and self.container[self.key].etag != etag:
            raise ValueError("ETag mismatch")
        self.container[self.key] = StateBasedDecider.StoredValue(
            state=self.serializer(state), etag=etag
        )


class EventSourcingDecider(interfaces.Decider):
    @dataclasses.dataclass()
    class EventsStream:
        events: list[interfaces.DeciderAggregate.Event] = dataclasses.field(
            default_factory=list
        )
        version: int = 0

    class DictBasedEventStore:
        def __init__(self) -> None:
            self.storage: dict[str, "EventSourcingDecider.EventsStream"] = {}

        def load_stream(self, key: str) -> "EventSourcingDecider.EventsStream":
            if key not in self.storage:
                return EventSourcingDecider.EventsStream()
            return self.storage[key]

        def append_to_stream(
            self,
            key: str,
            expected_version: int,
            events: list[interfaces.DeciderAggregate.Event],
        ) -> None:
            if expected_version > 0:
                current_stream = self.storage[key]
                if current_stream.version != expected_version:
                    raise RuntimeError("Concurrent stream write")
                current_stream.version += len(events)
                current_stream.events.extend(events)
                self.storage[key] = current_stream
            else:
                stream = EventSourcingDecider.EventsStream(events, len(events))
                self.storage[key] = stream

    def __init__(self, aggregate: interfaces.DeciderAggregate, key: str) -> None:
        self.event_store = EventSourcingDecider.DictBasedEventStore()
        self.key = key
        self.aggregate = aggregate

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.aggregate})"

    def decide(
        self, command: interfaces.DeciderAggregate.Command
    ) -> list[interfaces.DeciderAggregate.Event]:
        event_stream = self.event_store.load_stream(self.key)
        if event_stream.version == 0:
            state = self.aggregate.initial_state()
        else:
            state = fold(
                self.aggregate.evolve,
                self.aggregate.initial_state(),
                event_stream.events,
            )
        events = self.aggregate.decide(command, state)
        self.event_store.append_to_stream(self.key, event_stream.version, events)
        return events

    @property
    def state(self) -> interfaces.DeciderAggregate.State:
        event_stream = self.event_store.load_stream(self.key)
        state = fold(
            self.aggregate.evolve, self.aggregate.initial_state(), event_stream.events
        )
        return state
