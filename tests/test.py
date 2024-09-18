import unittest

from decider import compose_decider_aggregates
from deciders.bulb import Bulb
from deciders.cat import Cat
from infra import EventSourcingDecider, InMemoryDecider, StateBasedDecider
from serializers import (
    bulb_deserializer,
    bulb_serializer,
    cat_deserializer,
    cat_serializer,
)


class BulbTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cat_and_bulb = compose_decider_aggregates(Cat, Bulb)

        self.deciders = [
            InMemoryDecider(Bulb),
            StateBasedDecider(Bulb, bulb_serializer, bulb_deserializer, {}, "bulb"),
            EventSourcingDecider(Bulb, "bulb"),
            InMemoryDecider(self.cat_and_bulb),
        ]

    def test_fit_bulb(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given a bulb that is not fitted
                expected_events = [Bulb.FittedEvent(max_uses=5)]

                # When I fit the bulb
                command = Bulb.FitCommand(max_uses=5)
                result = decider.decide(command)

                # Then I get the Bulb Fitted event
                self.assertEqual(result, expected_events)

    def test_switch_on_bulb(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given a bulb that is fitted
                decider.decide(Bulb.FitCommand(max_uses=5))  # Set initial state
                expected_events = [Bulb.SwitchedOnEvent()]

                # When I switch on the bulb
                command = Bulb.SwitchOnCommand()
                result = decider.decide(command)

                # Then I get the Bulb SwitchedOn event
                self.assertEqual(result, expected_events)

    def test_bulb_switch_on_again(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given a bulb that is fitted
                decider.decide(
                    Bulb.FitCommand(max_uses=1)
                )  # Set bulb to blow after one use
                # And the bulb is switched on
                decider.decide(Bulb.SwitchOnCommand())  # Use the bulb once

                # When I switch on the bulb again
                command = Bulb.SwitchOnCommand()
                result = decider.decide(command)

                # Then nothing should happen
                self.assertEqual(result, [])

    def test_bulb_blew(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given a bulb that is fitted
                decider.decide(
                    Bulb.FitCommand(max_uses=1)
                )  # Set bulb to blow after one use
                # And the bulb is switched on
                decider.decide(Bulb.SwitchOnCommand())  # Use the bulb once

                # When I switch off the bulb
                decider.decide(Bulb.SwitchOffCommand())
                # And turn it on again
                result = decider.decide(Bulb.SwitchOnCommand())

                # Then I get the Bulb Blew event
                expected_events = [Bulb.BlewEvent()]
                self.assertEqual(result, expected_events)

    def test_blown_bulb_does_not_react_to_commands(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given a blown bulb
                decider.decide(Bulb.FitCommand(max_uses=0))
                decider.decide(Bulb.SwitchOnCommand())

                # When I switch on the bulb
                command = Bulb.SwitchOnCommand()
                result = decider.decide(command)

                # Then nothing should happen
                self.assertEqual(result, [])
                # When I switch off the bulb
                command = Bulb.SwitchOffCommand()
                result = decider.decide(command)

                # Then nothing should happen
                self.assertEqual(result, [])

    def test_blown_state_is_terminal(self):
        self.assertTrue(Bulb.is_terminal(Bulb.BlownState()))
        self.assertFalse(Bulb.is_terminal(Bulb.NotFittedState()))


class CatTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.deciders = [
            InMemoryDecider(Cat),
            StateBasedDecider(Cat, cat_serializer, cat_deserializer, {}, "cat"),
            EventSourcingDecider(Cat, "cat"),
        ]

    def test_is_terminal(self):
        self.assertFalse(Cat.is_terminal(Cat.AwakeState()))
        self.assertFalse(Cat.is_terminal(Cat.AsleepState()))

    def test_initial_state_view(self):
        # Given no events
        # When I ask for the initial state
        # Then I get the initial state
        self.assertEqual(Cat.initial_state(), Cat.AwakeState())

    def test_wake_up_command_initial_state_change(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given no events
                # When I command the cat to wake up
                command = Cat.WakeUpCommand()
                result = decider.decide(command)
                # Then nothing happens, as the cat is awake
                self.assertEqual(result, [])

    def test_go_to_sleep_command_state_change(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given no events
                # When I command the cat to go to sleep
                command = Cat.GoToSleepCommand()
                result = decider.decide(command)
                # Then cat goes to leep
                self.assertEqual(result, [Cat.GotToSleepEvent()])

    def test_got_to_sleep_state_view(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given cat is asleep
                command = Cat.GoToSleepCommand()
                decider.decide(command)
                # When I ask for the state
                # Then I get the cat is asleep
                self.assertEqual(decider.state, Cat.AsleepState())

    def test_wake_up_command_state_change(self):
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # Given cat is asleep
                command = Cat.GoToSleepCommand()
                decider.decide(command)
                # When I command the cat to wake up
                command = Cat.WakeUpCommand()
                result = decider.decide(command)
                # Then cat wakes up
                self.assertEqual(result, [Cat.WokeUpEvent()])
