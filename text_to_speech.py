import pyttsx3

def init_engine():
    # Forcer le driver Windows
    engine = pyttsx3.init(driverName='sapi5')

    # Essayer de trouver une voix française
    voices = engine.getProperty('voices')
    for v in voices:
        ident = (v.id + " " + v.name).lower()
        if "fr" in ident or "french" in ident:
            engine.setProperty('voice', v.id)
            break

    engine.setProperty('rate', 400)
    return engine

engine = init_engine()

texte = (
    "Bonjour Nicolas, comment vas-tu?"
    "Hello Nicolas, how are you this morning?"
    "Buongiorno Nicolas, come stai stamattina?"
    "Hallo Nicolas, hoe gaat het met je vanmorgen?"
)

engine.say(texte)
engine.runAndWait()
engine.stop()
