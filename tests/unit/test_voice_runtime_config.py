from src.voice_runtime_config import resolve_audio_device_index


def test_resolve_audio_device_index_returns_none_for_empty_value():
    assert resolve_audio_device_index("") is None
    assert resolve_audio_device_index("   ") is None
    assert resolve_audio_device_index(None) is None


def test_resolve_audio_device_index_parses_numeric_string():
    assert resolve_audio_device_index("0") == 0
    assert resolve_audio_device_index("7") == 7
    assert resolve_audio_device_index(" 12 ") == 12


def test_resolve_audio_device_index_rejects_invalid_value():
    try:
        resolve_audio_device_index("usb microphone")
    except ValueError as exc:
        assert "AUDIO_INPUT_DEVICE" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid device value")
