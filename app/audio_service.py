import time
from pathlib import Path

# Simple sound playback using pygame if available; fallback to no‑op.
try:
    from pygame import mixer
    _HAS_MIXER = True
except Exception:
    _HAS_MIXER = False

_SOUND_PATH = Path(__file__).parent.parent / "sound" / "warningsound.mp3"

if _HAS_MIXER:
    try:
        mixer.init()
    except Exception:
        _HAS_MIXER = False

_is_playing = False

def play_warning_sound() -> None:
    """Start playing warning sound on a loop. Safe to call repeatedly."""
    global _is_playing
    if not _HAS_MIXER or not _SOUND_PATH.is_file():
        return
    if _is_playing:
        return  # already looping, don't restart
    try:
        mixer.music.load(str(_SOUND_PATH))
        mixer.music.play(loops=-1)  # infinite loop
        _is_playing = True
    except Exception as e:
        print(f"Warning sound playback error: {e}")

def stop_warning_sound() -> None:
    """Stop warning sound immediately."""
    global _is_playing
    if not _HAS_MIXER:
        return
    if not _is_playing:
        return
    try:
        mixer.music.stop()
    except Exception as e:
        print(f"Warning sound stop error: {e}")
    _is_playing = False
