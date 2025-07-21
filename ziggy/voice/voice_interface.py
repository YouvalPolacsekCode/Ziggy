import speech_recognition as sr
from gtts import gTTS
from langdetect import detect
import playsound
import tempfile
import os
import time
import threading

import ctypes
import sys

# Suppress ALSA errors on Linux safely
import ctypes
import sys
from ctypes.util import find_library

# Global ref to prevent GC
_alsa_error_handler = None

def suppress_alsa_errors():
    global _alsa_error_handler
    try:
        asound = ctypes.cdll.LoadLibrary(find_library('asound'))
        CMPFUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
        _alsa_error_handler = CMPFUNC(lambda msg: None)  # Keep reference
        asound.snd_lib_error_set_handler(_alsa_error_handler)
        print("[INFO] ALSA error suppression active.")
    except Exception as e:
        print(f"[WARN] Failed to suppress ALSA errors: {e}", file=sys.stderr)

class VoiceAssistant:
    def __init__(self, language="auto", mic_index=1):
        suppress_alsa_errors()  # 🔊 Suppress ALSA logs before initializing audio
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Optional: tweak this too
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5
        self.listening_config = {
            "wake_word": {"ambient_duration": 0.5, "timeout": 4, "phrase_time_limit": 4},
            "command": {"ambient_duration": 1, "timeout": 10, "phrase_time_limit": 10}
        }

        try:
            self.microphone = sr.Microphone(device_index=mic_index)
        except Exception as e:
            print(f"[MIC INIT ERROR] {e}")
            self.microphone = None

    def _detect_language(self, text):
        try:
            lang = detect(text)
            return "he" if lang.startswith("he") else "en"
        except:
            return "en"

    def say(self, text, force_lang=None):
        lang = force_lang or (self._detect_language(text) if self.language == "auto" else self.language)
        try:
            if lang == "he":
                lang = "iw"
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts.save(fp.name)
                print(f"🟢 Ziggy says: {text}")
                def _play_audio_silently(filepath):
                    import subprocess
                    subprocess.Popen(
                        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    # Then use this:
                    threading.Thread(target=_play_audio_silently, args=(fp.name,), daemon=True).start()

        except Exception as e:
            print(f"[TTS ERROR] {e}")
            fallback = "לא הצלחתי לדבר" if lang == "he" else "I couldn't speak"
            os.system(f'espeak "{fallback}"')

    def _capture_audio(self, mode="command"):
        config = self.listening_config.get(mode, self.listening_config["command"])
        self.recognizer.pause_threshold = 0.8 if mode == "wake_word" else 0.5
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=config["ambient_duration"])
            print(f"🟢 Listening ({mode})...")
            try:
                start = time.time()
                audio = self.recognizer.listen(
                    source,
                    timeout=config["timeout"],
                    phrase_time_limit=config["phrase_time_limit"]
                )
                duration = time.time() - start
                print(f"[AUDIO] Capture duration: {duration:.2f}s")
                return audio
            except sr.WaitTimeoutError:
                print("⏰ Timeout: No speech detected.")
                return None

    def _recognize(self, audio):
        try:
            result = self.recognizer.recognize_google(audio, language="he-IL")
            return result, "he"
        except sr.UnknownValueError:
            try:
                result = self.recognizer.recognize_google(audio, language="en-US")
                return result, "en"
            except sr.UnknownValueError:
                return None, None
        except sr.RequestError as e:
            print(f"⚠️ Recognition error: {e}")
            return None, None

    def _matches_wake_word(self, text):
        lowered = text.lower()
        return any(phrase in lowered for phrase in [
            "hey ziggy", "ziggy", "היי זיגי", "הי זיגי"
        ])

    def listen_for_wake_word(self):
        if not self.microphone:
            print("[MIC ERROR] Microphone not initialized")
            return None

        print("🔁 Waiting for wake word...")
        audio = self._capture_audio(mode="wake_word")
        if not audio:
            return None

        result, lang = self._recognize(audio)
        print(f"[DEBUG] Wake word recognition result: {result}")

        if result and self._matches_wake_word(result):
            print("✅ Wake word detected.")
            return lang

        # Fallback: accept partial short phrases like just "Ziggy" or "היי"
        if result and len(result.split()) <= 2:
            print("🟡 Partial wake word match, accepting anyway.")
            return lang

        print("🔇 Wake word not detected.")
        return None

    def listen_for_command(self):
        if not self.microphone:
            print("[MIC ERROR] Microphone not initialized")
            return None

        print("🎙️ Awaiting command...")
        audio = self._capture_audio(mode="command")
        if not audio:
            return None

        result, lang = self._recognize(audio)
        if result:
            print(f"🗣️ You said: {result}")
            return result, lang

        print("❌ Didn’t catch that.")
        return None

    def listen_and_process(self, command_callback):
        while True:
            try:
                lang = self.listen_for_wake_word()
                if not lang:
                    continue
                self.say("כן?" if lang == "he" else "Yes?", force_lang=lang)
                command = self.listen_for_command()
                if command:
                    text, lang = command
                    command_callback(text, lang)
            except KeyboardInterrupt:
                print("\n👋 Exiting voice assistant.")
                break
