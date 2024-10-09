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
        self.cat_and_2_bulbs = compose_decider_aggregates(
            Cat, compose_decider_aggregates(Bulb, Bulb)
        )

        self.deciders = [
            InMemoryDecider(Bulb),
            StateBasedDecider(Bulb, bulb_serializer, bulb_deserializer, {}, "bulb"),
            EventSourcingDecider(Bulb, "bulb"),
            InMemoryDecider(self.cat_and_bulb),
            EventSourcingDecider(self.cat_and_bulb, "cat_and_bulb"),
            InMemoryDecider(self.cat_and_2_bulbs),
            EventSourcingDecider(self.cat_and_2_bulbs, "cat_and_2_bulbs"),
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
        self.cat_and_bulb = compose_decider_aggregates(Cat, Bulb)
        self.cat_and_2_bulbs = compose_decider_aggregates(
            Cat, compose_decider_aggregates(Bulb, Bulb)
        )
        self.deciders = [
            InMemoryDecider(Cat),
            StateBasedDecider(Cat, cat_serializer, cat_deserializer, {}, "cat"),
            EventSourcingDecider(Cat, "cat"),
            InMemoryDecider(self.cat_and_bulb),
            EventSourcingDecider(self.cat_and_bulb, "cat_and_bulb"),
            InMemoryDecider(self.cat_and_2_bulbs),
            EventSourcingDecider(self.cat_and_2_bulbs, "cat_and_2_bulbs"),
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


class CatAndBulbTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cat_and_bulb = compose_decider_aggregates(Cat, Bulb)
        self.deciders = [
            InMemoryDecider(self.cat_and_bulb),
            StateBasedDecider(Cat, cat_serializer, cat_deserializer, {}, "cat"),
            EventSourcingDecider(self.cat_and_bulb, "cat_and_bulb"),
        ]

    def test_combo(self) -> None:
        for decider in self.deciders:
            with self.subTest(decider=str(decider)):
                # cat wakes up
                self.assertEqual(
                    decider.decide(Cat.WakeUpCommand()), [Cat.WokeUpEvent()]
                )
                # cat goes to sleep
                self.assertEqual(
                    decider.decide(Cat.GoToSleepCommand()), [Cat.GotToSleepEvent()]
                )
                # bulb is fitted
                self.assertEqual(
                    decider.decide(Bulb.FitCommand(max_uses=5)), [Bulb.FittedEvent()]
                )
                # bulb is on
                self.assertEqual(
                    decider.decide(Bulb.SwitchOnCommand()), [Bulb.OnEvent()]
                )
                # bulb is off
                self.assertEqual(
                    decider.decide(Bulb.SwitchOffCommand()), [Bulb.OffEvent()]
                )


# class ComposedDeciderTests(unittest.TestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.in_memory_decider = InMemoryDecider(Either(Cat, Bulb))
#         self.state_based_decider = StateBasedDecider(
#             Either(Cat, Bulb),
#             cat_serializer,
#             bulb_serializer,
#             {},
#             "composed-cat-bulb",
#         )
#         self.event_sourcing_decider = EventSourcingDecider(
#             Either(Cat, Bulb), "composed-cat-bulb"
#         )

#         self.deciders = [
#             self.in_memory_decider,
#             self.state_based_decider,
#             self.event_sourcing_decider,
#         ]

#     def test_cat_wakeup_and_sleep(self):
#         for decider in self.deciders:
#             with self.subTest(decider=str(decider)):
#                 # Given no events initially
#                 # When I wake up the cat
#                 cat_wakeup_command = Either(left=Cat.WakeUpCommand())
#                 result_wakeup = decider.decide(cat_wakeup_command)
#                 # Then the cat wakes up
#                 self.assertEqual(result_wakeup, [Cat.WokeUpEvent()])

#                 # When I put the cat to sleep
#                 cat_sleep_command = Either(left=Cat.GoToSleepCommand())
#                 result_sleep = decider.decide(cat_sleep_command)
#                 # Then the cat goes to sleep
#                 self.assertEqual(result_sleep, [Cat.GotToSleepEvent()])


# #     def test_bulb_fit_and_switch(self):
# #         for decider in self.deciders:
# #             with self.subTest(decider=str(decider)):
# #                 # Given no events initially
# #                 # When I fit the bulb
# #                 bulb_fit_command = Either(right=Bulb.FitCommand(max_uses=5))
# #                 result_fit = decider.decide(bulb_fit_command)
# #                 # Then the bulb gets fitted
# #                 self.assertEqual(result_fit, [Bulb.FittedEvent(max_uses=5)])

# #                 # When I switch on the bulb
# #                 bulb_switch_on_command = Either(right=Bulb.SwitchOnCommand())
# #                 result_switch_on = decider.decide(bulb_switch_on_command)
# #                 # Then the bulb switches on
# #                 self.assertEqual(result_switch_on, [Bulb.SwitchedOnEvent()])

# #                 # When I switch off the bulb
# #                 bulb_switch_off_command = Either(right=Bulb.SwitchOffCommand())
# #                 result_switch_off = decider.decide(bulb_switch_off_command)
# #                 # Then the bulb switches off
# #                 self.assertEqual(result_switch_off, [Bulb.SwitchedOffEvent()])

# #     def test_cat_and_bulb_in_sequence(self):
# #         for decider in self.deciders:
# #             with self.subTest(decider=str(decider)):
# #                 # Given no events initially
# #                 # When I wake up the cat
# #                 result_wakeup = decider.decide(Either(left=Cat.WakeUpCommand()))
# #                 self.assertEqual(result_wakeup, [Cat.WokeUpEvent()])

# #                 # When I fit the bulb
# #                 result_fit = decider.decide(Either(right=Bulb.FitCommand(max_uses=5)))
# #                 self.assertEqual(result_fit, [Bulb.FittedEvent(max_uses=5)])

# #                 # When I switch on the bulb
# #                 result_switch_on = decider.decide(Either(right=Bulb.SwitchOnCommand()))
# #                 self.assertEqual(result_switch_on, [Bulb.SwitchedOnEvent()])

# #                 # When I put the cat to sleep
# #                 result_sleep = decider.decide(Either(left=Cat.GoToSleepCommand()))
# #                 self.assertEqual(result_sleep, [Cat.GotToSleepEvent()])

# #     def test_state_persisted_cat_and_bulb(self):
# #         # Testing state persistence with composed deciders
# #         for decider in self.deciders:
# #             with self.subTest(decider=str(decider)):
# #                 # Given no events initially
# #                 # When I fit the bulb
# #                 decider.decide(Either(right=Bulb.FitCommand(max_uses=5)))

# #                 # When I put the cat to sleep
# #                 decider.decide(Either(left=Cat.GoToSleepCommand()))

# #                 # Re-initialize the decider to simulate persistence
# #                 reloaded_decider = StateBasedDecider(
# #                     Either(Cat, Bulb),
# #                     cat_serializer,
# #                     bulb_serializer,
# #                     decider.container,
# #                     "composed-cat-bulb",
# #                 )

# #                 # Check if state is still valid after reloading
# #                 self.assertEqual(
# #                     reloaded_decider.state,
# #                     (Cat.AsleepState(), Bulb.WorkingState("Off", 5)),
# #                 )


# # class ManyCatsTests(unittest.TestCase):
# #     def setUp(self) -> None:
# #         super().setUp()
# #         self.in_memory_many_cats = InMemoryDecider(Either(Cat))
# #         self.state_many_cats = StateBasedDecider(
# #             Either(Cat),
# #             cat_serializer,
# #             cat_deserializer,
# #             {},
# #             "many-cats",
# #         )

# #     def test_many_cats_in_memory(self):
# #         # Testing multiple cat states in memory
# #         self.in_memory_many_cats.decide(Either(left=("Boulette", Cat.WakeUpCommand())))
# #         self.in_memory_many_cats.decide(
# #             Either(left=("Guevara", Cat.GoToSleepCommand()))
# #         )

# #         # Check if Boulette is awake
# #         self.assertEqual(self.in_memory_many_cats.state["Boulette"], Cat.AwakeState())
# #         # Check if Guevara is asleep
# #         self.assertEqual(self.in_memory_many_cats.state["Guevara"], Cat.AsleepState())

# #     def test_many_cats_with_state_persistence(self):
# #         # Testing multiple cat states with state persistence
# #         self.state_many_cats.decide(Either(left=("Boulette", Cat.WakeUpCommand())))
# #         self.state_many_cats.decide(Either(left=("Guevara", Cat.GoToSleepCommand())))

# #         # Simulate persistence by re-initializing
# #         reloaded_decider = StateBasedDecider(
# #             Either(Cat),
# #             cat_serializer,
# #             cat_deserializer,
# #             self.state_many_cats.container,
# #             "many-cats",
# #         )

# #         # Check if Boulette is awake
# #         self.assertEqual(reloaded_decider.state["Boulette"], Cat.AwakeState())
# #         # Check if Guevara is asleep
# #         self.assertEqual(reloaded_decider.state["Guevara"], Cat.AsleepState())
