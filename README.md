# Ziggy 1.0 – Smart Home AI Assistant

Ziggy is a multilingual, AI-powered smart home assistant running on Raspberry Pi. It responds to voice commands, integrates with smart home devices, manages lists and tasks, and supports a conversational mode via GPT. Ziggy 1.0 is modular, local-first, and highly customizable.

---

## ✅ CURRENT FEATURES (Implemented)

### 🗣️ Voice Interface
- Supports Hebrew 🇮🇱 and English 🇺🇸 voice input and responses (via gTTS and langdetect)
- Wake word: "Hey Ziggy" or "היי זיגי"
- Mixed-language detection and handling
- Adjustable ambient noise calibration and timeouts
- Text and speech output for all responses

### 🤖 Intent Parser
- Hybrid system using:
  - Regex-based quick parsing
  - GPT-based fallback parsing for complex commands
- Supported intents:
  - `get_time`, `get_date`, `get_weather`
  - `tell_joke`, `tell_fact`, `generate_idea`
  - `control_device` (on/off devices)
  - `create_task`, `cancel_task`, `set_reminder`
  - `save_memory`, `ask_memory`
  - `read_file`, `write_file`, `add_to_list`, `remove_from_list`
  - `run_ifttt`, `switch_mode`, `play_music`, `ask_health`
  - `exit`, `restart`, `shutdown_system`, `reboot_system`
  - `debug_diagnostics`, `get_status`, `chat_with_gpt`

### 🧠 Memory & Knowledge
- Persistent memory manager for saving/retrieving topics
- GPT fallback when memory lacks an answer

### 📝 File System Integration
- Create, read, and update local files
- Supports TODO/grocery lists and editable logs

### ⏱️ Task & Reminder System
- Create and cancel tasks with natural language
- Local scheduling planned (currently placeholder)

### 🌐 Telegram Bot (Fully Functional)
- Respond to Ziggy via Telegram (read, reply, execute)
- Secure token-based access
- Runs concurrently with voice interface

---

## ⚙️ SYSTEM ARCHITECTURE

- `ziggy_main.py`: Boot script, intent handler, parallel process runner
- `voice_interface.py`: Handles all voice input/output
- `intent_parser.py`: Detects and routes user intents
- `telegram_bot.py`: Receives and responds to Telegram commands
- `memory_manager.py`: Saves and retrieves long-term memory
- `task_manager.py`: Manages simple task scheduling
- `file_manager.py`: Reads/writes TXT, JSON, MD, etc.
- `ifttt_handler.py`: Triggers IFTTT webhooks
- `device_controller.py`: Placeholder for smart device control

---

## 🔜 FUTURE WORK (Roadmap)

### 🏡 Smart Home Automation
- Integrate Zigbee sensors/devices via Zigpy or Home Assistant
- Control lights, AC, switches with context-aware commands
- Add real-time state sync + Ziggy status summaries
- Support routines: “Good night”, “I’m home”, etc.

### 🔌 Home Assistant Integration
- Use MQTT, WebSocket, or REST API
- Support both voice and Telegram control
- Fetch states and trigger automations via Ziggy

### 🛠️ Device Diagnostics
- Local system health: CPU load, temperature, disk usage
- Device pings: check smart device responsiveness
- Water leak, motion detection via Zigbee sensors

### 🧠 Buddy Mode (GPT Chat)
- Reflective journaling, support talk, memory-based Q&A
- Proactive suggestions and conversation history awareness

### 🔒 Roles & Security
- Multi-user roles: Admin, Trusted, Guest
- Command permissions
- Remote kill switch, audit logs

### 📱 Mobile Access
- Full Telegram integration (done)
- Future: Web dashboard + mobile app view

---

## 🛠️ SETUP INSTRUCTIONS

1. Clone repo: `git clone https://github.com/YouvalPolacsekCode/Ziggy.git`
2. Install dependencies from `requirements.txt`
3. Set mic index (via `arecord -l`) and update `VoiceAssistant(mic_index=N)`
4. Add your `.env` or `settings.yaml` with:
   ```
   openai:
     api_key: sk-xxx
   telegram:
     bot_token: <token>
     allowed_user_id: <your_telegram_id>
   ```
5. Run: `python3 ziggy_main.py`

---

## 👨‍🔧 RECOMMENDED HARDWARE

- Raspberry Pi 5 (8 GB)
- High-efficiency heatsink + fan
- USB Microphone
- JBL Flip (or similar Bluetooth speaker)
- Zigbee USB stick (e.g. Sonoff Zigbee 3.0)
- Ethernet connection for stability

---

## 📂 STRUCTURE

```
ziggy/
├── core/
│   ├── ziggy_main.py
│   ├── intent_parser.py
│   └── chatgpt.py
├── voice/
│   └── voice_interface.py
├── integrations/
│   ├── telegram_bot.py
│   └── ifttt_handler.py
├── smart_home/
│   └── device_controller.py
├── tasks/
│   └── task_manager.py
├── memory/
│   └── memory_manager.py
├── files/
│   └── file_manager.py
└── config/
    └── settings.yaml
```

---

## 🧪 TESTED & FUNCTIONAL

✅ Wake word  
✅ Telegram bot  
✅ GPT fallback logic  
✅ Voice STT + TTS  
✅ Memory & list persistence  
✅ File editing  
✅ Intent parsing  
✅ Concurrent voice + Telegram  
✅ Hebrew + English mixed handling  

---

## 🧠 NEXT STEPS (For Developer)

- Implement Home Assistant or Zigbee control via `device_controller`
- Expand task_manager for real scheduling (via APScheduler or asyncio)
- Add proactive reminders or state-based triggers
- Use webhooks to sync state or send alerts
- Enhance fallback responses using `chat_with_gpt`
- Finalize roles and user permission system

---

## LICENSE

Ziggy is a personal assistant framework developed by Youval. Use freely, but attribution appreciated.
