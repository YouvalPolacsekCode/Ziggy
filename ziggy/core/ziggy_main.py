#!/usr/bin/env python3
"""
Ziggy 1.0 – main entry point
"""
import sys
import os
import time
import threading
from datetime import datetime
import pytz

import contextlib

# ── FULL STDERR SUPPRESSION FOR JACK/ALSA ───────────────────────────────────────
def suppress_audio_stderr():
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        print("[INFO] Audio stderr suppression active.")
    except Exception as e:
        print(f"[WARN] Could not suppress audio stderr: {e}", file=sys.stderr)

suppress_audio_stderr()

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


# Environment and timezone setup
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["SDL_AUDIODRIVER"] = "dsp"
os.environ["TZ"] = "UTC"
os.environ["JACK_NO_AUDIO_RESERVATION"] = "1"
time.tzset()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# ✅ Import settings from intent_parser
from core.intent_parser import settings

# ── Core Ziggy modules ──────────────────────────────────────────────────────────
from voice.voice_interface import VoiceAssistant
from core import intent_parser
from memory import memory_manager
from smart_home import device_controller
from integrations import ifttt_handler
from tasks import task_manager
from files import file_manager

# ── Command router ─────────────────────────────────────────────────────────────
def handle_command(text: str, lang: str) -> None:
    parsed = intent_parser.parse(text)
    intent = parsed.get("intent")
    params = parsed.get("params", {})

    print(f"[INTENT] {intent} | Params: {params}")

    def say_auto(msg_he, msg_en):
        voice.say(msg_he if lang == "he" else msg_en)

    if intent == "get_time":
        say_auto("השעה עכשיו " + datetime.now().strftime("%H:%M"),
                 "The time is now " + datetime.now().strftime("%H:%M"))

    elif intent == "get_date":
        say_auto("היום " + datetime.now().strftime("%A, %B %d"),
                 "Today is " + datetime.now().strftime("%A, %B %d"))

    elif intent == "get_weather":
        location = params.get("location") or "your location"
        say_auto(f"מזג האוויר ב־{location} הוא שמשי ונעים",
                 f"The weather in {location} is sunny and pleasant")

    elif intent == "control_device":
        device = params.get("device")
        action = params.get("action")
        if device and action:
            if action == "on":
                device_controller.turn_on(device)
                say_auto(f"{device} הופעל", f"{device} turned on")
            elif action == "off":
                device_controller.turn_off(device)
                say_auto(f"{device} כובה", f"{device} turned off")
        else:
            say_auto("יש לציין שם התקן ופעולה", "Please specify device and action")

    elif intent == "chat_with_gpt":
        prompt = params.get("text", "")
        if prompt:
            from core.chatgpt import get_gpt_reply
            reply = get_gpt_reply(prompt)
            voice.say(reply)

    elif intent == "ask_memory":
        topic = params.get("topic")
        content = memory_manager.retrieve(topic)
        if content:
            voice.say(content)
        else:
            # Fallback to GPT
            from openai import OpenAI
            gpt_client = OpenAI(api_key=settings["openai"]["api_key"])
            try:
                response = gpt_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Who is {topic}?"}],
                    temperature=0.5
                )
                reply = response.choices[0].message.content.strip()
                voice.say(reply)
            except Exception as e:
                print(f"[GPT Fallback Error] {e}")
                voice.say("לא הצלחתי למצוא תשובה")

    elif intent == "add_to_list":
        item = params.get("item")
        if item:
            file_manager.add_to_list(item)
            say_auto(f"{item} נוסף לרשימה", f"{item} added to list")

    elif intent == "remove_from_list":
        item = params.get("item")
        if item:
            file_manager.remove_from_list(item)
            say_auto(f"{item} הוסר מהרשימה", f"{item} removed from list")

    elif intent == "create_task":
        desc = params.get("description")
        when = params.get("when")
        if desc and when:
            task_manager.create_task(desc, when)
            say_auto(f"יצרתי משימה: {desc} ל־{when}", f"Created task: {desc} at {when}")

    elif intent == "cancel_task":
        desc = params.get("description")
        if desc:
            task_manager.cancel_task(desc)
            say_auto(f"מחקתי את המשימה: {desc}", f"Deleted task: {desc}")

    elif intent == "save_memory":
        memory_manager.save(params.get("topic"), params.get("content"))
        say_auto("שמרתי את זה בזיכרון", "Saved to memory")

    elif intent == "read_file":
        content = file_manager.read(params.get("filename"))
        say_auto("התוכן הוא: " + content[:200], "The content is: " + content[:200])

    elif intent == "write_file":
        file_manager.write(params.get("filename"), params.get("content"))
        say_auto("קובץ עודכן", "File updated")

    elif intent == "tell_joke":
        say_auto("למה שלדים לא נלחמים אחד בשני? כי אין להם אומץ!",
                 "Why don’t skeletons fight each other? They don’t have the guts!")

    elif intent == "tell_fact":
        say_auto("ידעת שלתמנון יש שלושה לבבות?", "Did you know an octopus has three hearts?")

    elif intent == "generate_idea":
        say_auto("רעיון: לבנות מראה חכמה שמדברת איתך", "Idea: build a smart mirror that talks to you")

    elif intent == "get_status":
        say_auto("כל המערכות פועלות כראוי", "All systems are operational")

    elif intent == "exit":
        say_auto("להתראות", "Goodbye")
        exit(0)

    elif intent == "restart":
        say_auto("מאתחל...", "Restarting...")
        os.execv(sys.executable, ['python3'] + sys.argv)

    elif intent in ("run_ifttt", "ifttt_trigger"):
        ifttt_handler.trigger(params.get("event"), params.get("value1"))
        say_auto("אירוע IFTTT הופעל", "IFTTT event triggered")

    elif intent == "switch_mode":
        mode = params.get("mode")
        say_auto(f"עובר למצב {mode}... (טרם נתמך)", f"Switching to mode {mode}... (not yet supported)")

    elif intent == "ask_buddy":
        say_auto("אני מקשיב, בוא נדבר על זה", "I'm listening, let's talk about it")

    elif intent == "set_reminder":
        say_auto(f"תזכורת נקבעה ל־{params.get('when')}: {params.get('message')}",
                 f"Reminder set for {params.get('when')}: {params.get('message')}")

    elif intent == "play_music":
        song = params.get("song", "שיר מרגיע")
        say_auto(f"מנגן {song}... (תמיכה תגיע בהמשך)", f"Playing {song}... (support coming soon)")

    elif intent == "ask_health":
        say_auto(f"אני לא רופא, אבל הנה מה שמצאתי על {params.get('issue')}...",
                 f"I'm not a doctor, but here's what I found about {params.get('issue')}...")

    elif intent == "debug_diagnostics":
        say_auto("מריץ אבחון מערכתי...", "Running diagnostics...")

    elif intent == "translate":
        say_auto(f"מתרגם '{params.get('text')}' ל־{params.get('target_lang')}...",
                 f"Translating '{params.get('text')}' to {params.get('target_lang')}...")

    elif intent == "shutdown_system":
        say_auto("מכבה את המערכת...", "Shutting down the system...")
        os.system("sudo shutdown now")

    elif intent == "reboot_system":
        say_auto("מאתחל את המערכת...", "Rebooting the system...")
        os.system("sudo reboot")

    else:
        say_auto("לא הבנתי את הבקשה", "I didn't understand the request")

# ── Boot and Threaded Runtime ───────────────────────────────────────────────────

def start_voice_listener():
    voice.listen_and_process(handle_command)

def start_telegram_bot():
    from integrations.telegram_bot import run_bot
    run_bot()

if __name__ == "__main__":
    print("🚀 Ziggy is booting…")

    suppress_audio_stderr()  # Only suppress during audio startup
    voice = VoiceAssistant(language="auto", mic_index=1)

    memory_manager.load_memory()
    voice.say("זיגי מוכן")

    voice_thread = threading.Thread(target=start_voice_listener)
    telegram_thread = threading.Thread(target=start_telegram_bot)

    voice_thread.start()
    telegram_thread.start()

    voice_thread.join()
    telegram_thread.join()
