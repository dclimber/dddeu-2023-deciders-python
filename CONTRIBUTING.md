# How to contribute

1. Please port stuff from [run.fsx]([run.fsx#L102](https://github.com/thinkbeforecoding/dddeu-2023-deciders/blob/main/run.fsx))  to [test.py](./tests/test.py), so they can run with:
   - `make test` command

### TODOs, Some still unported stuff, with suggestions from ChatGPT:
The Python version of the F# `let neutral` decider can be written as follows. Since `neutral` in F# accepts no commands, emits no events, and has a single state (`unit` in F# translates to `None` or something similar in Python), we'll translate that behavior while respecting the structure defined in `DeciderAggregate`.

Here's the Python version of the `neutral` decider:

```python
from interfaces import DeciderAggregate


class NeutralDecider(DeciderAggregate):

    class VoidCommand(DeciderAggregate.Command):
        def decide(self, state: "NeutralDecider.State") -> list:
            return []

    class VoidEvent(DeciderAggregate.Event):
        pass

    class NeutralState(DeciderAggregate.State):
        def evolve(self, event: "NeutralDecider.Event") -> "NeutralDecider.State":
            return self

    # -- Methods --
    @classmethod
    def initial_state(cls) -> "NeutralDecider.State":
        return cls.NeutralState()

    @classmethod
    def is_terminal(cls, state: "NeutralDecider.State") -> bool:
        return True  # The state is always terminal in the neutral decider


# Create an instance of the neutral decider
neutral_decider = NeutralDecider()
```

### Explanation:
- **VoidCommand**: A command that does nothing and returns an empty list of events.
- **VoidEvent**: An event type that has no actual effect.
- **NeutralState**: A state that doesn’t evolve and always returns itself.
- **initial_state**: Returns a neutral state.
- **is_terminal**: Always returns `True`, since in the neutral decider, the state is terminal by definition (as no transitions or events are possible).

This Python implementation mirrors the behavior of the `neutral` decider from the F# code.

----

The F# `many` decider allows managing multiple instances of a decider, each indexed by a unique identifier (like a string). We'll translate this behavior into Python, using a `dict` to hold the states of each decider instance. Each decider can then be operated on independently by its unique identifier.

Here’s the Python version of the `many` function:

```python
from typing import Dict, Tuple
from interfaces import DeciderAggregate


class ManyDecider(DeciderAggregate):

    def __init__(self, decider: DeciderAggregate):
        self.decider = decider
        self.initial_state = {}

    class Command(DeciderAggregate.Command):
        def __init__(self, id: str, command: DeciderAggregate.Command):
            self.id = id
            self.command = command

        def decide(self, state: "ManyDecider.State") -> list:
            return state.decider_states[self.id].decide(state.get_decider_state(self.id))

    class Event(DeciderAggregate.Event):
        def __init__(self, id: str, event: DeciderAggregate.Event):
            self.id = id
            self.event = event

    class State(DeciderAggregate.State):
        def __init__(self, decider_states: Dict[str, DeciderAggregate.State]):
            self.decider_states = decider_states

        def evolve(self, event: "ManyDecider.Event") -> "ManyDecider.State":
            new_state = self.decider_states.copy()
            current_state = self.decider_states.get(event.id, ManyDecider.initial_state())
            new_state[event.id] = current_state.evolve(event.event)
            return ManyDecider.State(new_state)

        def get_decider_state(self, id: str) -> DeciderAggregate.State:
            return self.decider_states.get(id, ManyDecider.initial_state())

    @classmethod
    def initial_state(cls) -> "ManyDecider.State":
        return cls.State({})

    @classmethod
    def is_terminal(cls, state: "ManyDecider.State") -> bool:
        # If all individual deciders are in their terminal states, return True
        return all(
            cls.is_terminal(individual_state)
            for individual_state in state.decider_states.values()
        )

    def decide(self, command: "ManyDecider.Command", state: "ManyDecider.State") -> list:
        current_state = state.get_decider_state(command.id)
        events = self.decider.decide(command.command, current_state)
        return [(command.id, event) for event in events]

    def evolve(self, state: "ManyDecider.State", event: "ManyDecider.Event") -> "ManyDecider.State":
        return state.evolve(event)
```

### Explanation:
1. **Command Class**: This class wraps a command for an individual decider instance. It contains an identifier (`id`) that refers to the instance and a `command` that will be passed to the specific decider.
  
2. **Event Class**: Similar to `Command`, this class wraps an event for a specific instance by storing the identifier (`id`) and the actual `event`.

3. **State Class**: Holds a dictionary of decider states, where each state is indexed by a unique identifier. It provides methods to evolve the states or retrieve a state by its identifier. When evolving, it ensures that the correct instance's state is updated.

4. **Decider Methods**:
   - **initial_state**: Initializes with an empty dictionary to represent the initial state of all managed decider instances.
   - **is_terminal**: Checks if all decider instances have reached their terminal state.
   - **decide**: Routes the decision process to the specific decider instance identified by the command’s ID.
   - **evolve**: Evolves the state of the individual decider instance corresponding to the event’s ID.

This `ManyDecider` implementation allows multiple decider instances to be managed within a single decider aggregate. Each instance is identified by a unique ID and evolves independently based on its own commands and events.

-----

The `adapt` function in F# is used to adapt a decider to different types of commands, events, and states. It takes four transformation functions:
- `fci`: Converts new commands to the original command type (returns `None` if the command is not applicable).
- `fei`: Converts new events to the original event type (returns `None` if the event is not applicable).
- `feo`: Converts the original events to the new event type.
- `fsi`: Extracts the state from the new state structure.

Here’s how to translate this into Python:

```python
from typing import Callable, Optional, List
from interfaces import DeciderAggregate


class AdaptedDecider(DeciderAggregate):

    def __init__(
        self,
        fci: Callable[[DeciderAggregate.Command], Optional[DeciderAggregate.Command]],
        fei: Callable[[DeciderAggregate.Event], Optional[DeciderAggregate.Event]],
        feo: Callable[[DeciderAggregate.Event], DeciderAggregate.Event],
        fsi: Callable[[DeciderAggregate.State], DeciderAggregate.State],
        decider: DeciderAggregate
    ):
        self.fci = fci
        self.fei = fei
        self.feo = feo
        self.fsi = fsi
        self.decider = decider

    @classmethod
    def initial_state(cls) -> "DeciderAggregate.State":
        return cls.decider.initial_state()

    @classmethod
    def is_terminal(cls, state: "DeciderAggregate.State") -> bool:
        return cls.decider.is_terminal(cls.fsi(state))

    def decide(
        self, command: DeciderAggregate.Command, state: DeciderAggregate.State
    ) -> List[DeciderAggregate.Event]:
        adapted_command = self.fci(command)
        if adapted_command is not None:
            original_state = self.fsi(state)
            events = self.decider.decide(adapted_command, original_state)
            return [self.feo(event) for event in events]
        return []

    def evolve(
        self, state: DeciderAggregate.State, event: DeciderAggregate.Event
    ) -> DeciderAggregate.State:
        adapted_event = self.fei(event)
        if adapted_event is not None:
            original_state = self.fsi(state)
            new_state = self.decider.evolve(original_state, adapted_event)
            return new_state
        return self.fsi(state)
```

### Explanation:
1. **fci** (`command adapter`): Transforms an incoming command into the original command type that the `decider` understands. It returns `None` if the command is not applicable to the decider.
  
2. **fei** (`event adapter`): Transforms an incoming event into the original event type that the `decider` understands. It returns `None` if the event does not apply.
  
3. **feo** (`event output adapter`): Converts the events emitted by the `decider` back to the new event type.
  
4. **fsi** (`state adapter`): Extracts the state that is relevant to the `decider` from a larger or differently structured state.

### Methods:
- **`decide`**: Adapts a command using `fci`, applies the decider’s decision logic, and converts the resulting events using `feo`.
- **`evolve`**: Adapts an event using `fei`, evolves the state using the decider’s `evolve` method, and returns the evolved state.
- **`initial_state`** and **`is_terminal`**: Forward calls to the underlying decider, using `fsi` to extract the relevant state.

### Usage Example:
Suppose we have a decider that only works with certain types of commands and events, but we want to use it within a larger system that deals with a more complex set of commands, events, or states. The `adapt` function enables this transformation while preserving the behavior of the original decider.

This Python version mirrors the functionality of the F# `adapt` function and provides flexibility to adapt a decider's interface for different types of commands, events, and states.

------

In F#, the `map` and `map2` functions are used to apply a function to the return state(s) of a decider. In Python, we can implement these in a similar way, applying the function to the state produced by the `evolve` method of a decider.

Here's the Python version of the `map` and `map2` functions:

### Python Version of `map`

The `map` function applies a transformation function (`f`) to the state produced by the `evolve` method of the decider.

```python
from typing import Callable
from interfaces import DeciderAggregate


class MappedDecider(DeciderAggregate):
    def __init__(self, f: Callable[[DeciderAggregate.State], DeciderAggregate.State], decider: DeciderAggregate):
        self.f = f
        self.decider = decider

    @classmethod
    def initial_state(cls) -> DeciderAggregate.State:
        # Apply the transformation function to the initial state
        return cls.f(cls.decider.initial_state())

    @classmethod
    def is_terminal(cls, state: DeciderAggregate.State) -> bool:
        # Check if the original decider's state is terminal
        return cls.decider.is_terminal(state)

    def decide(self, command: DeciderAggregate.Command, state: DeciderAggregate.State) -> list:
        # Use the original decider's `decide` method
        return self.decider.decide(command, state)

    def evolve(self, state: DeciderAggregate.State, event: DeciderAggregate.Event) -> DeciderAggregate.State:
        # Apply the transformation function to the state produced by evolve
        new_state = self.decider.evolve(state, event)
        return self.f(new_state)
```

### Explanation:
- **`f`**: This is a function that transforms the state.
- **`decider`**: The original decider whose state is transformed by `f`.
- **`initial_state`**: The transformation function is applied to the initial state of the original decider.
- **`evolve`**: The function `f` is applied to the result of the `evolve` method of the original decider.

---

### Python Version of `map2`

The `map2` function takes two deciders and combines their return states using a function `f` that takes two states (`sx` and `sy`) and produces a combined state.

```python
from typing import Callable
from interfaces import DeciderAggregate


class MappedDecider2(DeciderAggregate):
    def __init__(
        self,
        f: Callable[[DeciderAggregate.State, DeciderAggregate.State], DeciderAggregate.State],
        decider_x: DeciderAggregate,
        decider_y: DeciderAggregate
    ):
        self.f = f
        self.decider_x = decider_x
        self.decider_y = decider_y

    @classmethod
    def initial_state(cls) -> DeciderAggregate.State:
        # Apply the combining function to the initial states of both deciders
        return cls.f(cls.decider_x.initial_state(), cls.decider_y.initial_state())

    @classmethod
    def is_terminal(cls, state: DeciderAggregate.State) -> bool:
        # Both deciders need to be in terminal state for the combined state to be terminal
        return cls.decider_x.is_terminal(state) and cls.decider_y.is_terminal(state)

    def decide(self, command: DeciderAggregate.Command, state: DeciderAggregate.State) -> list:
        # Combine the decisions from both deciders
        events_x = self.decider_x.decide(command, state)
        events_y = self.decider_y.decide(command, state)
        return events_x + events_y

    def evolve(self, state: DeciderAggregate.State, event: DeciderAggregate.Event) -> DeciderAggregate.State:
        # Evolve both deciders and combine their resulting states
        new_state_x = self.decider_x.evolve(state, event)
        new_state_y = self.decider_y.evolve(state, event)
        return self.f(new_state_x, new_state_y)
```

### Explanation:
- **`f`**: A function that combines two states into one.
- **`decider_x`, `decider_y`**: The two deciders whose states will be combined.
- **`initial_state`**: Combines the initial states of both deciders using the function `f`.
- **`decide`**: Collects the events produced by both deciders and combines them.
- **`evolve`**: Evolves both deciders and applies the function `f` to the results, combining the two evolved states.

---

### Example Usage:

Let's say you have two deciders, `decider_a` and `decider_b`. You can use `map` and `map2` like this:

```python
# Apply a transformation to the state of decider_a
mapped_decider = MappedDecider(lambda state: state_transformation(state), decider_a)

# Combine the states of decider_a and decider_b into a single state
combined_decider = MappedDecider2(lambda sx, sy: combine_states(sx, sy), decider_a, decider_b)
```

### Conclusion:

In this Python implementation:
- **`map`** is used to apply a transformation to the state returned by a single decider.
- **`map2`** is used to combine the states returned by two deciders using a combining function.

These functions give flexibility to work with deciders in a modular way by transforming or combining their return states.
