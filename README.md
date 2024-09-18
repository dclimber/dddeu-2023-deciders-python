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
