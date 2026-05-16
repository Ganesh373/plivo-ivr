from flask import Flask, request, Response
import plivo

app = Flask(__name__)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
AUTH_ID    = "MAYMYZMWEYNMM1YTA2MW"
AUTH_TOKEN = "ZjMwYTI5NmEtMWY2Zi00ZGZkLWEyZGUtZjM5MzZh"
PLIVO_NUMBER = "918035736861"   # From the assignment

# YOUR details — edit these
YOUR_NUMBER      = "91XXXXXXXX"   # ✅ your number
YOUR_OTP         = "XXXX"           # ← put your birthdate here
ASSOCIATE_NUMBER = "91XXXXXXXXXX"   # ✅ same as your number (for testing)
# Publicly accessible MP3 for audio playback
AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# ─── TRIGGER OUTBOUND CALL ────────────────────────────────────────────────────
@app.route("/make_call", methods=["GET", "POST"])
def make_call():
    """Initiates the outbound call from Plivo to your number."""
    client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)
    call = client.calls.create(
        from_=PLIVO_NUMBER,
        to_=YOUR_NUMBER,
        answer_url=request.host_url + "answer",
        answer_method="GET",
    )
    return f"<h2>Call initiated! UUID: {call['request_uuid']}</h2>"


# ─── STEP 1: ANSWER → ASK FOR OTP ────────────────────────────────────────────
@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Called by Plivo when the call is answered. Asks for OTP."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{base}verify_otp" method="GET" timeout="10" numDigits="4" retries="5">
        <Speak>Welcome to InspireWorks. Please enter your 4 digit O T P to continue.</Speak>
    </GetDigits>
    <Speak>We did not receive any input. Goodbye.</Speak>
    <Hangup/>
</Response>""".format(base=request.host_url)
    return Response(xml, mimetype="text/xml")


# ─── STEP 2: VERIFY OTP ───────────────────────────────────────────────────────
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    """Checks the entered OTP. Re-prompts if wrong, proceeds if correct."""
    digits = request.args.get("Digits", "")

    if digits == YOUR_OTP:
        # Correct OTP → go to Level 1 menu
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>O T P verified. Welcome!</Speak>
    <Redirect method="GET">{base}ivr_level1</Redirect>
</Response>""".format(base=request.host_url)
    else:
        # Wrong OTP → re-prompt
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{base}verify_otp" method="GET" timeout="10" numDigits="4" retries="5">
        <Speak>Incorrect O T P. Please try again. Enter your 4 digit O T P.</Speak>
    </GetDigits>
    <Speak>No input received. Goodbye.</Speak>
    <Hangup/>
</Response>""".format(base=request.host_url)

    return Response(xml, mimetype="text/xml")


# ─── STEP 3: LEVEL 1 — LANGUAGE SELECTION ────────────────────────────────────
@app.route("/ivr_level1", methods=["GET", "POST"])
def ivr_level1():
    """Level 1 IVR: Language selection."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{base}ivr_level2" method="GET" timeout="10" numDigits="1" retries="3">
        <Speak>Please select your language. Press 1 for English. Press 2 for Spanish.</Speak>
    </GetDigits>
    <Speak>No input received. Returning to language selection.</Speak>
    <Redirect method="GET">{base}ivr_level1</Redirect>
</Response>""".format(base=request.host_url)
    return Response(xml, mimetype="text/xml")


# ─── STEP 4: LEVEL 2 — ACTION MENU ───────────────────────────────────────────
@app.route("/ivr_level2", methods=["GET", "POST"])
def ivr_level2():
    """Level 2 IVR: Action menu (audio or connect to associate)."""
    language = request.args.get("Digits", "1")

    if language == "1":
        lang_name = "English"
    elif language == "2":
        lang_name = "Spanish"
    else:
        # Invalid language input → go back to Level 1
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Invalid selection. Please try again.</Speak>
    <Redirect method="GET">{base}ivr_level1</Redirect>
</Response>""".format(base=request.host_url)
        return Response(xml, mimetype="text/xml")

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{base}ivr_action?lang={lang}" method="GET" timeout="10" numDigits="1" retries="3">
        <Speak>You selected {lang_name}. Press 1 to listen to an audio message. Press 2 to connect to a live associate.</Speak>
    </GetDigits>
    <Speak>No input received. Returning to menu.</Speak>
    <Redirect method="GET">{base}ivr_level2?Digits={lang}</Redirect>
</Response>""".format(base=request.host_url, lang=language, lang_name=lang_name)
    return Response(xml, mimetype="text/xml")


# ─── STEP 5: HANDLE ACTION ────────────────────────────────────────────────────
@app.route("/ivr_action", methods=["GET", "POST"])
def ivr_action():
    """Handles the final action: play audio or connect to associate."""
    action = request.args.get("Digits", "")
    lang   = request.args.get("lang", "1")

    if action == "1":
        # Play audio message
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Playing your audio message now.</Speak>
    <Play>{audio}</Play>
    <Speak>Thank you for calling InspireWorks. Goodbye.</Speak>
    <Hangup/>
</Response>""".format(audio=AUDIO_URL)

    elif action == "2":
        # Connect to live associate
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Please hold. Connecting you to a live associate.</Speak>
    <Dial callerId="{plivo_num}">
        <Number>{associate}</Number>
    </Dial>
    <Speak>The associate is unavailable. Goodbye.</Speak>
    <Hangup/>
</Response>""".format(plivo_num=PLIVO_NUMBER, associate=ASSOCIATE_NUMBER)

    else:
        # Invalid input → go back to Level 2
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Invalid selection. Please try again.</Speak>
    <Redirect method="GET">{base}ivr_level2?Digits={lang}</Redirect>
</Response>""".format(base=request.host_url, lang=lang)

    return Response(xml, mimetype="text/xml")


# ─── RUN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
