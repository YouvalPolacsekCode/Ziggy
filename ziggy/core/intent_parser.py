import os
import json
import yaml
import re
import openai
from openai import OpenAI
from datetime import datetime

# Load config
def load_settings():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

settings = load_settings()
client = OpenAI(api_key=settings["openai"]["api_key"])

# ── Regex-based quick parser ─────────────────────────────────────
def quick_parse(text):
    text = text.lower()

    if re.search(r"\b(what.*time|current time|שעה)\b", text):
        return {"intent": "get_time", "params": {}}
    if re.search(r"\b(what.*date|today's date|תאריך)\b", text):
        return {"intent": "get_date", "params": {}}
    if re.search(r"\bweather\b|מזג אוויר", text):
        return {"intent": "get_weather", "params": {}}
    if re.search(r"\bjoke\b|בדיחה", text):
        return {"intent": "tell_joke", "params": {}}
    if re.search(r"\bfact\b|עובדה", text):
        return {"intent": "tell_fact", "params": {}}
    if re.search(r"\brestart\b|אתחל", text):
        return {"intent": "restart", "params": {}}
    if re.search(r"\bshutdown\b|כבה", text):
        return {"intent": "shutdown_system", "params": {}}
    return None

# ── GPT-based fallback parser ─────────────────────────────────────
def gpt_parse(text):
    prompt = f\"\"\"\nYou are a smart home assistant named Ziggy. Your task is to analyze user requests and extract the user's intent and any relevant parameters in a JSON object.

Here are the supported intents and their expected parameters:
- get_time: {{}}
- get_date: {{}}
- get_weather: {{\"location\": str (optional)}}
- control_device: {{\"device\": str, \"action\": \"on\"|\"off\"|\"toggle\"|\"set_brightness\"|\"set_temperature\" (and other relevant actions), \"value\": str (optional, e.g., brightness level, temperature)}}
- add_to_list: {{\"item\": str}}
- remove_from_list: {{\"item\": str}}
- create_task: {{\"description\": str, \"when\": str (natural time)}}
- cancel_task: {{\"description\": str}}
- ask_memory: {{\"topic\": str}}
- save_memory: {{\"topic\": str, \"content\": str}}
- read_file: {{\"filename\": str}}
- write_file: {{\"filename\": str, \"content\": str}}
- tell_joke: {{}}
- tell_fact: {{}}
- generate_idea: {{\"topic\": str}}
- get_status: {{}}
- exit: {{}}
- restart: {{}}
- run_ifttt: {{\"event\": str, \"value1\": str (optional)}}\n- switch_mode: {{\"mode\": str}}\n- ask_buddy: {{\"question\": str}}\n- set_reminder: {{\"message\": str, \"when\": str}}\n- play_music: {{\"song\": str (optional)}}
- ask_health: {{\"issue\": str}}
- debug_diagnostics: {{}}
- translate: {{\"text\": str, \"target_lang\": str}}
- shutdown_system: {{}}
- reboot_system: {{}}

For the 'control_device' intent, make sure to extract the 'device' name, the 'action' (like 'on', 'off', 'toggle', 'set_brightness', 'set_temperature'), and the 'value' if the user provides one (e.g., "set the living room light to 50 percent", the value is "50").

Always return a valid JSON object and nothing else. Do not include any extra text or formatting.

User: \"{text}\"
Ziggy (JSON):
\"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[INTENT PARSER ERROR] {e}")
        return {"intent": "unknown", "params": {}}

# ── Public parse function ─────────────────────────────────────────
def parse(text):
    result = quick_parse(text)
    if result:
        return result
    return gpt_parse(text)

# ── Sample direct handler (for testing/chat mode) ────────────────
def handle_command(text, context=None):
    result = parse(text)
    intent = result.get("intent")
    params = result.get("params", {})
    print(f"[Intent] {intent} | [Params] {params}")

    if intent == "get_time":
        return f"The current time is {datetime.now().strftime('%H:%M')}"
    elif intent == "get_weather":
        location = params.get("location", "your area")
        return f"I'll get the weather for {location} soon."
    elif intent == "tell_joke":
        return "Why don’t scientists trust atoms? Because they make up everything."
    elif intent == "restart":
        os.system("sudo reboot")
        return "🔁 Restarting system..."
    elif intent == "shutdown_system":
        os.system("sudo shutdown now")
        return "🛑 Shutting down..."
    
    return "I'm not sure what you meant. Please try again."
