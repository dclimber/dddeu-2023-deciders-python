import unittest

from deciders.bulb import Bulb
from deciders.cat import Cat
from infra import InMemoryDecider


class BulbTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.decider = InMemoryDecider(Bulb)

    def test_fit_bulb(self):
        # Given a bulb that is not fitted
        expected_events = [Bulb.FittedEvent(max_uses=5)]

        # When I fit the bulb
        command = Bulb.FitCommand(max_uses=5)
        result = self.decider.decide(command)

        # Then I get the Bulb Fitted event
        self.assertEqual(result, expected_events)

    def test_switch_on_bulb(self):
        # Given a bulb that is fitted
        self.decider.decide(Bulb.FitCommand(max_uses=5))  # Set initial state
        expected_events = [Bulb.SwitchedOnEvent()]

        # When I switch on the bulb
        command = Bulb.SwitchOnCommand()
        result = self.decider.decide(command)

        # Then I get the Bulb SwitchedOn event
        self.assertEqual(result, expected_events)

    def test_bulb_switch_on_again(self):
        # Given a bulb that is fitted
        self.decider.decide(
            Bulb.FitCommand(max_uses=1)
        )  # Set bulb to blow after one use
        # And the bulb is switched on
        self.decider.decide(Bulb.SwitchOnCommand())  # Use the bulb once

        # When I switch on the bulb again
        command = Bulb.SwitchOnCommand()
        result = self.decider.decide(command)

        # Then nothing should happen
        self.assertEqual(result, [])

    def test_bulb_blew(self):
        # Given a bulb that is fitted
        self.decider.decide(
            Bulb.FitCommand(max_uses=1)
        )  # Set bulb to blow after one use
        # And the bulb is switched on
        self.decider.decide(Bulb.SwitchOnCommand())  # Use the bulb once

        # When I switch off the bulb
        self.decider.decide(Bulb.SwitchOffCommand())
        # And turn it on again
        result = self.decider.decide(Bulb.SwitchOnCommand())

        # Then I get the Bulb Blew event
        expected_events = [Bulb.BlewEvent()]
        self.assertEqual(result, expected_events)

    def test_blown_bulb_does_not_react_to_commands(self):
        # Given a blown bulb
        self.decider.decide(Bulb.FitCommand(max_uses=0))
        self.decider.decide(Bulb.SwitchOnCommand())

        # When I switch on the bulb
        command = Bulb.SwitchOnCommand()
        result = self.decider.decide(command)

        # Then nothing should happen
        self.assertEqual(result, [])
        # When I switch off the bulb
        command = Bulb.SwitchOffCommand()
        result = self.decider.decide(command)

        # Then nothing should happen
        self.assertEqual(result, [])

    def test_blown_state_is_terminal(self):
        self.assertTrue(Bulb.is_terminal(Bulb.BlownState()))
        self.assertFalse(Bulb.is_terminal(Bulb.NotFittedState()))


class CatTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.decider = InMemoryDecider(Cat)

    def test_is_terminal(self):
        self.assertFalse(Cat.is_terminal(Cat.AwakeState()))
        self.assertFalse(Cat.is_terminal(Cat.AsleepState()))

    def test_initial_state_view(self):
        # Given no events
        # When I ask for the initial state
        # Then I get the initial state
        self.assertEqual(Cat.initial_state(), Cat.AwakeState())

    def test_wake_up_command_initial_state_change(self):
        # Given no events
        # When I command the cat to wake up
        command = Cat.WakeUpCommand()
        result = self.decider.decide(command)
        # Then nothing happens, as the cat is awake
        self.assertEqual(result, [])

    def test_go_to_sleep_command_state_change(self):
        # Given no events
        # When I command the cat to go to sleep
        command = Cat.GoToSleepCommand()
        result = self.decider.decide(command)
        # Then cat goes to leep
        self.assertEqual(result, [Cat.GotToSleepEvent()])

    def test_got_to_sleep_state_view(self):
        # Given cat is asleep
        command = Cat.GoToSleepCommand()
        self.decider.decide(command)
        # When I ask for the state
        # Then I get the cat is asleep
        self.assertEqual(self.decider.state, Cat.AsleepState())

    def test_wake_up_command_state_change(self):
        # Given cat is asleep
        command = Cat.GoToSleepCommand()
        self.decider.decide(command)
        # When I command the cat to wake up
        command = Cat.WakeUpCommand()
        result = self.decider.decide(command)
        # Then cat wakes up
        self.assertEqual(result, [Cat.WokeUpEvent()])
