# Aggregate Composition: A New View on Aggregates

This repository contains an educational implementation of **Aggregate Composition** in **Event Sourcing** using Python. The focus is on the **Decider pattern**, which combines multiple deciders to model complex domain logic in a clean and scalable way. It is based on the original [F# repository](https://github.com/thinkbeforecoding/dddeu-2023-deciders/) by [Jérémie Chassaing](https://github.com/thinkbeforecoding), ported to Python for learning and experimentation purposes.

> **Note**: This repository is for **educational purposes only**. It demonstrates the concepts of **Aggregate Composition** in **Event Sourcing** and is not intended for production use.

## State of the Project
As of **2024-09-18**, the `main` branch is at the `41:48` mark of the lecture: _"Combining Deciders"_.

## [Lecture](https://www.youtube.com/watch?v=72TOhMpEVlA) Notes:
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
    - Listens to events, produces commands, and has internal states  
        - Whenever lights are switched on, awake the cat  
46:55 - Combining Process with the Decider  
    - Takes a process from the decider that is Cat and Bulb combo  
        - `react` - one or multiple commands  
        - Recursion: collect all events from decider until no more events to process  
51:30 - Application layer  
51:55 - No need to change the Aggregate!  
52:25 - How you run the decider is independent of the domain  

## Getting Started

### Prerequisites

- Python 3.x
- Basic understanding of Event Sourcing, Aggregates, and the Decider pattern

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/aggregate-composition-python
    ```

### Running the Project

Running the project is done by simply running unit tests with

```bash
make test
```

command.

## Contributing

Contributions are welcome! Please check the [CONTRIBUTING.md](./CONTRIBUTING.md) file for detailed guidelines on how to contribute to this project.

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for more details.

---

**Disclaimer:** This repository is intended for educational purposes only. The examples and implementations are simplified to illustrate key concepts of Aggregate Composition and Event Sourcing in Python. They are not optimized for production use.
