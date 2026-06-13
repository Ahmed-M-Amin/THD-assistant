from unittest.mock import Mock, patch

import numpy as np

from src.live_chat_worker import LiveChatWorker
from src.local_voice_handler import LocalVoiceHandler


def test_local_voice_handler_uses_selected_microphone_device():
    handler = LocalVoiceHandler(device_index=7, sample_rate=16000)
    handler.recognizer = Mock()
    handler.recognizer.listen.side_effect = Exception("stop after microphone setup")

    microphone = Mock()
    microphone.__enter__ = Mock(return_value=Mock())
    microphone.__exit__ = Mock(return_value=False)

    with patch("src.local_voice_handler.sr.Microphone", return_value=microphone) as mic:
        try:
            handler.listen_once(language="en")
        except Exception:
            pass

    mic.assert_called_once_with(device_index=7, sample_rate=16000)


def test_live_chat_worker_uses_voice_pipeline_for_captured_audio():
    voice_handler = Mock()
    voice_handler.sample_rate = 16000
    voice_handler.listen_once.side_effect = [("", np.array([0.1, -0.1], dtype=np.float32))]

    manager = Mock()
    manager.process_voice_query.return_value = ("hello", "Hi there", b"audio")

    session = {"messages": []}
    worker = LiveChatWorker(
        voice_handler=voice_handler,
        manager=manager,
        language="en",
        session=session,
        save_session=Mock(),
    )

    voice_handler.play_audio_interruptible.side_effect = lambda *args, **kwargs: worker.stop_event.set()

    worker._run_loop()

    manager.process_voice_query.assert_called_once()
    manager.process_text_query.assert_not_called()
    args, kwargs = manager.process_voice_query.call_args
    assert np.array_equal(args[0], np.array([0.1, -0.1], dtype=np.float32))
    assert kwargs["preferred_language"] == "en"
    assert kwargs["sample_rate"] == 16000
    assert session["messages"] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
