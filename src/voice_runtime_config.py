"""Helpers for wiring configured voice settings into runtime components."""


def resolve_audio_device_index(value) -> int | None:
    """Parse AUDIO_INPUT_DEVICE from settings into an int device index or None."""
    if value is None:
        return None

    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        if trimmed.isdigit():
            return int(trimmed)
        raise ValueError(
            "AUDIO_INPUT_DEVICE must be empty or a numeric microphone device index."
        )

    if isinstance(value, int):
        return value

    raise ValueError(
        "AUDIO_INPUT_DEVICE must be empty or a numeric microphone device index."
    )
