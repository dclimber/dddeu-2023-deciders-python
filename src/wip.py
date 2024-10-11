import dataclasses
from typing import Generic, Literal, TypeVar
from abc import ABC, abstractmethod
from collections.abc import Iterable

E = TypeVar("E")
C = TypeVar("C")
S = TypeVar("S")
EX = TypeVar("EX")
CX = TypeVar("CX")
SX = TypeVar("SX")
EY = TypeVar("EY")
CY = TypeVar("CY")
SY = TypeVar("SY")


class BaseEvent(ABC):
    pass


class BaseCommand(ABC):
    pass


class BaseState(ABC):
    pass


class Aggregate(ABC, Generic[E, S]):
    class Event(BaseEvent):
        pass

    class Command(BaseCommand):
        pass

    class State(BaseState):
        pass

    @property
    @abstractmethod
    def initial_state(self) -> S:
        raise NotImplementedError()

    @abstractmethod
    def evolve(self, s: S, e: E) -> S:
        pass

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        pass


class Process(Aggregate[E, S], Generic[E, S, C]):
    @abstractmethod
    def react(self, s: S, e: E) -> Iterable[C]:
        pass

    @abstractmethod
    def resume(self, s: S) -> Iterable[C]:
        pass


class Decider(Aggregate[E, S], Generic[E, C, S]):
    @abstractmethod
    def decide(self, c: C, s: S) -> Iterable[E]:
        pass


class CatAggregate(Aggregate[Aggregate.State, Aggregate.Event]):
    # Custom cat events
    class Event(Aggregate.Event):
        pass

    class Command(Aggregate.Command):
        pass

    class State(Aggregate.State):
        pass

    class Wakeup(Command):
        pass

    class GetToSleep(Command):
        pass

    class WokeUp(Event):
        pass

    class GotToSleep(Event):
        pass

    class Awake(State):
        pass

    class Asleep(State):
        pass

    @property
    def initial_state(self):
        return self.Awake()

    def evolve(self, s, e):
        match (s, e):
            case (self.Awake(), self.GotToSleep()):
                return self.Asleep()
            case (self.Asleep(), self.WokeUp()):
                return self.Awake()
            case _:
                return s

    def is_terminal(self, s):
        return False


class CatDecider(
    Decider[CatAggregate.Event, CatAggregate.Command, CatAggregate.State],
    CatAggregate,  # NOQA: E501
):
    def decide(self, c: CatAggregate.Command, s: CatAggregate.State):
        match c, s:
            case (CatAggregate.Wakeup(), CatAggregate.Asleep()):
                return [CatAggregate.WokeUp()]
            case (CatAggregate.GetToSleep(), CatAggregate.Awake()):
                return [CatAggregate.GotToSleep()]
            case _:
                return []


class BulbAggregate(Aggregate[Aggregate.State, Aggregate.Event]):
    @dataclasses.dataclass(frozen=True)
    class Event(Aggregate.Event):
        pass

    @dataclasses.dataclass(frozen=True)
    class Command(Aggregate.Command):
        pass

    @dataclasses.dataclass(frozen=True)
    class State(Aggregate.State):
        pass

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

    @dataclasses.dataclass(frozen=True)
    class NotFittedState(State):
        pass

    @dataclasses.dataclass(frozen=True)
    class WorkingState(State):
        status: Literal["On", "Off"]
        remaining_uses: int

    @dataclasses.dataclass(frozen=True)
    class BlownState(State):
        pass

    @dataclasses.dataclass(frozen=True)
    class FitCommand(Command):
        max_uses: int

    class SwitchOnCommand(Command):
        pass

    class SwitchOffCommand(Command):
        pass

    @property
    def initial_state(self):
        return self.NotFittedState()

    def evolve(self, s, e):
        match (s, e):
            case (self.NotFittedState(), self.FittedEvent()):
                return self.WorkingState(
                    status="On", remaining_uses=e.max_uses
                )  # NOQA: E501
            case (self.WorkingState(), self.SwitchedOnEvent()):
                return self.WorkingState(
                    status="On", remaining_uses=s.remaining_uses - 1
                )
            case (self.WorkingState(), self.SwitchedOffEvent()):
                return self.WorkingState(
                    status="Off", remaining_uses=s.remaining_uses
                )  # NOQA: E501
            case (self.WorkingState(), self.BlewEvent()):
                return self.BlewEvent()
            case _:
                return s

    def is_terminal(self, s):
        return isinstance(s, self.BlownState)


class BulbDecider(
    Decider[BulbAggregate.Event, BulbAggregate.Command, BulbAggregate.State],
    BulbAggregate,
):
    def decide(self, c: BulbAggregate.Command, s: BulbAggregate.State):
        match (c, s):
            case (BulbAggregate.FitCommand(), BulbAggregate.NotFittedState()):
                return [BulbAggregate.FittedEvent(max_uses=c.max_uses)]
            case (
                BulbAggregate.SwitchOnCommand(),
                BulbAggregate.WorkingState(status="Off", remaining_uses=n),
            ) if n > 0:
                return [BulbAggregate.SwitchedOnEvent()]
            case (
                BulbAggregate.SwitchOnCommand(),
                BulbAggregate.WorkingState(status="Off"),
            ):
                return [BulbAggregate.BlewEvent()]
            case (
                BulbAggregate.SwitchedOffEvent(),
                BulbAggregate.WorkingState(status="On"),
            ):
                return [BulbAggregate.SwitchedOffEvent()]
            case _:
                return []


class CatLight(Process[Aggregate.Event, Aggregate.State, Aggregate.Command]):
    @dataclasses.dataclass(frozen=True)
    class Event(Aggregate.Event):
        pass

    @dataclasses.dataclass(frozen=True)
    class Command(Aggregate.Command):
        pass

    @dataclasses.dataclass(frozen=True)
    class State(Aggregate.State):
        pass

    class SwitchedOn(Event):
        pass

    class WokeUp(Event):
        pass

    class WakeUp(Command):
        pass

    class Idle(State):
        pass

    class WakingUp(State):
        pass

    def evolve(self, s: Aggregate.State, e: Aggregate.Event):
        match e:
            case self.SwitchedOn():
                return self.WakingUp()
            case self.WakeUp():
                return self.Idle()

    def resume(self, s):
        match s:
            case self.WakingUp():
                return [self.WakeUp()]
            case _:
                return []

    @property
    def initial_state(self):
        return self.Idle()

    def is_terminal(self, s):
        return isinstance(s, self.Idle())

    def react(self, s, e):
        match (s, e):
            case (self.WakingUp(), self.SwitchedOn):
                return [self.WakeUp()]
            case _:
                return []


class ApplicativeCompose(
    Decider[Aggregate.Command, Aggregate.Event, Aggregate.Event]
):  # NOQA: E501
    def decide(self, c, s):
        match c:
            case BulbAggregate.SwitchedOnEvent():
                return CatLight.SwitchedOn()
            case CatAggregate.WokeUp():
                return CatLight.WakeUp()

    # let comboProc =
    #     Process.combineWithDecider
    #         (Process.adapt
    #             (function
    #                 | Bulb Bulb.SwitchedOn -> Some CatLight.SwitchedOn
    #                 | Cat Cat.WokeUp -> Some CatLight.WokeUp
    #                 | _ -> None)
    #             (function CatLight.WakeUp -> Cat Cat.WakeUp)
    #             CatLight.proc)
    #         combo


def compose(
    dx: Decider[CX, EX, SX], dy: Decider[CY, EY, SY]
) -> Decider[Aggregate.Command, Aggregate.Event, Aggregate.State]:
    class ComposedDecider(
        Decider[Aggregate.Command, Aggregate.Event, Aggregate.State]
    ):  # NOQA: E501

        def decide(self, c, s):
            match c:
                case dx.Command():
                    return dx.decide(c, s)
                case dy.Command():
                    return dy.decide(c, s)
            print(dx.Command)

        def evolve(self, s, e):
            match e:
                case dx.Event():
                    return dx.evolve(s, e)
                case dy.Event():
                    return dy.evolve(s, e)

        def is_terminal(self, s):
            return dx.is_terminal() and dy.is_terminal()

        @property
        def initial_state(self) -> Aggregate.State:
            raise NotImplementedError()  # todo: Composite type <SY, SX>

    return ComposedDecider()


def combine_process_with_decider(
    process: Process[E, S, C], decider: Decider[CY, EY, SY]
) -> Decider[CY, EY, tuple[S, SY]]:
    class ProcessDecider(
        Decider[Aggregate.Event, Aggregate.Command, tuple[S, SY]]
    ):  # NOQA: E501

        def collect_fold(
            self,
            process: Process[Aggregate.Event, Aggregate.State, Aggregate.Command],
            state: Aggregate.State,
            events: list[Aggregate.Event],
        ) -> list[Aggregate.Command]:
            commands: list[Aggregate.Command] = []
            while len(events) > 0:
                event = events.pop(0)
                state = process.evolve(state, events.pop(0))
                for cmd in process.react(state, event):
                    commands.append(cmd)
            return commands

        def decide(self, c, s: tuple[S, SY]) -> Iterable[Aggregate.Event]:
            (process_state, decider_state) = s
            commands = [c]
            events: list[Aggregate.Event] = []
            while len(commands) > 0:
                command = commands.pop(0)
                for event in decider.decide(command, decider_state):
                    events.append(event)
                for cmd in self.collect_fold(self.process, process_state, events):
                    commands.append(cmd)
            return events

    return ProcessDecider()


if __name__ == "__main__":
    cb = compose(CatDecider(), BulbDecider())
    print(cb)
    bulb_event = cb.decide(
        BulbAggregate.SwitchOnCommand(),
        BulbAggregate.WorkingState(status="Off", remaining_uses=3),
    )[0]
    cat_event = cb.decide(CatAggregate.Wakeup(), CatAggregate.Asleep())[0]
    assert isinstance(bulb_event, BulbAggregate.SwitchedOnEvent)
    assert isinstance(cat_event, CatAggregate.WokeUp)
    # cl = CatLight()
    # print(cl.initial_state)
    # print(cl.decide(CatAggregate.GetToSleep(), CatAggregate.Awake()))


# // Structure for a process
# type Process<'e,  'c, 's> =
#     { evolve: 's -> 'e -> 's
#       resume: 's -> 'c list
#       react: 's -> 'e -> 'c list
#       initialState: 's
#       isTerminal: 's -> bool }

# // this process wakes up the cat when the bulb is switched on
# // (of course the can will no be got to sleep when the bulb is switched off...)
# module CatLight =

#     type Event =
#     | SwitchedOn
#     | WokeUp

#     type Command =
#     | WakeUp

#     type State =
#     | Idle
#     | WakingUp


#     let proc =
#         { evolve =
#             fun state event ->
#                 match event with
#                 | SwitchedOn -> WakingUp
#                 | WokeUp -> Idle

#           resume = fun state ->
#             match state with
#             | WakingUp -> [WakeUp]
#             | _ -> []

#           react = fun state event ->
#             match state, event with
#             | WakingUp, SwitchedOn -> [WakeUp]
#             | _ -> []

#           initialState = Idle

#           isTerminal = fun s -> s = Idle
#         }

# module Process =
#     // change the input events and output commands types of the process
#     let adapt selectEvent convertCommand (p: Process<_,_,_>) =
#         { evolve =
#             fun state event ->
#                 match selectEvent event with
#                 | Some e -> p.evolve state e
#                 | None -> state
#           resume =
#             fun state ->
#                 p.resume state |> List.map convertCommand

#           react =
#              fun state event ->
#                 match selectEvent event with
#                 | Some e ->
#                     p.react state e |> List.map convertCommand
#                 | None -> []
#           initialState = p.initialState

#           isTerminal = p.isTerminal
#         }

#     // fold state and collect commands returned by the react function
#     let collectFold (proc: Process<'e,'c,'s>) (state: 's) (events: 'e list) : 'c list =
#         let rec loop state events allCommands =
#             match events with
#             | [] -> allCommands
#             | event :: rest ->
#                 let newState = proc.evolve state event
#                 let cmds = (proc.react newState event)
#                 loop newState rest (allCommands @ cmds)
#         loop state events []

#     // combine a process with a decider
#     let combineWithDecider (proc: Process<'e,'c,'ps>) (decider: Decider<'c,'e,'ds>) : Decider<'c,'e,'ds * 'ps> =
#         { decide =
#             fun cmd (ds, ps) ->
#                 let rec loop cmds allEvents =
#                     match cmds with
#                     | [] -> allEvents
#                     | cmd :: rest ->
#                         let events = decider.decide cmd ds
#                         let newCmds = collectFold proc ps events
#                         loop (rest @ newCmds) (allEvents @ events)

#                 loop [cmd] []
#           evolve =
#             fun (ds, ps) event ->
#                 (decider.evolve ds event), proc.evolve ps event

#           initialState = decider.initialState, proc.initialState

#           isTerminal = fun (ds, ps) -> decider.isTerminal ds && proc.isTerminal ps
#         }
