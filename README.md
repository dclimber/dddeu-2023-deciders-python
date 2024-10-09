# Aggregate composition: a new view on Aggregates

**Original [F# repository](https://github.com/thinkbeforecoding/dddeu-2023-deciders/) by [Jérémie Chassaing](https://github.com/thinkbeforecoding)**


**State**: As of 2024-09-18 the `main` branch is at `41:48` mark of the lecture: "Combining deciders"

### [Lecture](https://www.youtube.com/watch?v=72TOhMpEVlA) notes:
0:14 - Intro
1:01 - Aggregate Composition
3:48 - Decider pattern
9:53 - Aggregate examples
14:08 - Tests
16:47 - Running in memory
22:23 - Persisting the state
29:27 - Event Sourcing variant
32:00 - Single Decider
38:42 - Cat and Bulb Decider
40:59 - Cat and Bulb in memory
41:35 - Combining deciders
41:48 - Neutral decider for creating monoidal deciders based on the Decider Composer
43:03 - Many Deciders
45:15 - Process (State machine)
    listens to events, produces commands, has internal states
        whenever lights is switched on, awake the cat
46:55 - Combining Process with the Decider
    take a process from the decider that is Cat and the Bulb combo
        `react` - one or multiple commands
            until no events to process
                recursion! - collect all events from decider
51:30 - application layer
51:55 - no need to change the Aggregate!
52:25 - how you run the decider is independent of the domain

This is the code of the talk presented at [DDDEu 2023](https://2023.dddeurope.com/) in the EventSourcingLive track.

It starts with the [definition of a decider](./deciders.fsx#L5).

Then it defines two simple deciders, [a bulb](./deciders.fsx#L16) and [a cat](./deciders.fsx#LL72C4-L72C4).

[Some tests](./src/test.py) check the behavior of both deciders.

The rest of the [run.fsx](run.fsx#L102) file uses the deciders using functions from infra.fsx to run deciders [in memory](infra.fsx#L14), [persisting state](infra.fsx#L62) or [persisting events](infra.fsx#L74).


Deciders are composed using the [combine function](run.fsx#L141), the [many function](./run.fsx#L244) and composed with [a process](run.fsx#L284).

Finally, deciders are composed in a custom way using [applicative functor](run.fsx#L308).

