# Plivo IVR Demo — InspireWorks

A Flask-based IVR system built with Plivo's Voice API.

## Features
- Outbound call trigger
- OTP authentication (birthdate in DDMM format)
- Level 1: Language selection (English / Spanish)
- Level 2: Play audio OR connect to live associate

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Edit `app.py` — fill in YOUR details
Open `app.py` and update these 3 lines near the top:

```python
YOUR_NUMBER       = "91XXXXXXXXXX"   # Your phone number (no + or spaces), e.g. 919876543210
YOUR_OTP          = "1503"           # Your birthdate in DDMM format, e.g. 15 March → 1503
ASSOCIATE_NUMBER  = "91XXXXXXXXXX"   # Any placeholder number for "live associate"
```

### 3. Start the Flask app
```bash
python app.py
```
Flask will run on `http://localhost:5000`

### 4. Expose it to the internet with ngrok
In a **new terminal**, run:
```bash
ngrok http 5000
```
You'll get a URL like `https://abc123.ngrok-free.app` — copy it.

> **Why ngrok?** Plivo's servers need to reach your app over the internet. ngrok creates a public tunnel to your localhost.

### 5. Make the call
Open your browser and go to:
```
https://abc123.ngrok-free.app/make_call
```
Your phone will ring within a few seconds!

---

## Plivo Credentials (from assignment)
```
Auth ID    : MAYMYZMWEYNMM1YTA2MW
Auth Token : ZjMwYTI5NmEtMWY2Zi00ZGZkLWEyZGUtZjM5MzZh
Plivo No.  : +91 80 3573 6861
```

---

## Call Flow

```
Call answered
    ↓
Enter 4-digit OTP (your birthdate DDMM)
    ↓ wrong → re-prompt
    ↓ correct
Level 1: Press 1 (English) / Press 2 (Spanish)
    ↓
Level 2: Press 1 (Play audio) / Press 2 (Connect to associate)
```

---

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /make_call` | Triggers the outbound call |
| `GET /answer` | Called by Plivo on call answer |
| `GET /verify_otp` | Checks OTP input |
| `GET /ivr_level1` | Language selection menu |
| `GET /ivr_level2` | Action menu |
| `GET /ivr_action` | Plays audio or connects associate |

---

## Demo Video Checklist
- [ ] Show `/make_call` triggering the call
- [ ] Enter wrong OTP first → hear re-prompt
- [ ] Enter correct OTP → hear "OTP verified"
- [ ] Press 1 or 2 for language
- [ ] Press 1 to hear audio / Press 2 to forward call
