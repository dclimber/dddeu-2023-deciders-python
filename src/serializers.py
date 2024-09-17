import interfaces
from deciders import bulb, cat


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
