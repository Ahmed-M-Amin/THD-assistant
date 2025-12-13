# Manual Testing Checklist for Voice Features

## Why Manual Testing?
Voice features (STT/TTS) are difficult to automate because:
- Microphone simulation is complex and environment-dependent
- Audio quality assessment is subjective
- Real-world noise conditions vary
- Edge-TTS and SpeechRecognition require actual audio I/O

---

## Test Scenarios

### 1. Microphone Detection & Calibration
**Steps**:
1. Launch app: `streamlit run Home.py`
2. Navigate to Assistant page
3. Select "🎤 Live Chat" mode
4. Click "▶️ Start Live Chat"

**Expected**:
- [ ] No "AudioDeviceError" appears
- [ ] "🔴 Listening... Speak now!" message displays
- [ ] No immediate timeout errors

**Notes**: _____________________________________

---

### 2. Basic Speech Recognition (English)
**Steps**:
1. Start Live Chat
2. Speak clearly: **"What are the tuition fees for international students?"**
3. Wait for bot response

**Expected**:
- [ ] Your speech is transcribed correctly (check chat history)
- [ ] Bot responds with fee information
- [ ] Bot asks which program you're interested in

**Actual Transcription**: _____________________________________

**Notes**: _____________________________________

---

### 3. Speech Recognition - THD Terminology
**Steps**:
1. Start Live Chat
2. Speak: **"I want to apply to THD for a bachelor's in business administration"**
3. Check transcription

**Expected**:
- [ ] "THD" is recognized (not misheard as "tihari", "tea", etc.)
- [ ] "bachelor's" is correct (not "batchel", "batch law")
- [ ] "administration" is correct (not "administration")

**Actual Transcription**: _____________________________________

**Notes**: _____________________________________

---

### 4. Text-to-Speech Quality (Female Voice)
**Steps**:
1. Ask bot: "Tell me about the application process"
2. Listen to the TTS response

**Expected**:
- [ ] Voice is clear and understandable
- [ ] Speed is appropriate (not too fast/slow)
- [ ] No robotic artifacts or glitches
- [ ] "THD" is pronounced reasonably (not perfect, but acceptable)

**Rating (1-5)**: _____

**Notes**: _____________________________________

---

### 5. Multi-Turn Conversation
**Steps**:
1. Start Live Chat
2. Say: "What programs do you offer?"
3. Bot responds
4. Say: "Tell me more about the master's programs"
5. Bot responds
6. Say: "What are the requirements?"

**Expected**:
- [ ] All 3 questions are transcribed correctly
- [ ] Bot maintains context (references previous questions)
- [ ] No "didn't catch that" errors

**Context Maintained?**: _____________________________________

**Notes**: _____________________________________

---

### 6. Background Noise Handling
**Steps**:
1. Start Live Chat
2. Play background music or have TV on
3. Speak: "What are the fees?"

**Expected**:
- [ ] Bot still recognizes speech (may have errors)
- [ ] No complete failure to detect voice

**Success Rate**: _____________________________________

**Notes**: _____________________________________

---

### 7. Goodbye / Exit Command
**Steps**:
1. Start Live Chat
2. Say: "Goodbye"

**Expected**:
- [ ] Live chat stops automatically
- [ ] "Goodbye!" message appears
- [ ] Session is saved to history

**Notes**: _____________________________________

---

## Environment Info
- **Date Tested**: _____________________________________
- **OS**: Windows
- **Microphone**: _____________________________________
- **Background Noise Level**: Quiet / Moderate / Loud
- **Tester**: _____________________________________

---

## Known Issues (Track Here)
1. _____________________________________
2. _____________________________________
3. _____________________________________

---

## Recommendations After Testing
- Should we adjust `energy_threshold` in `local_voice_handler.py`?
- Should we add more post-processing corrections?
- Is TTS voice preference acceptable or switch to male?

**Notes**: _____________________________________
