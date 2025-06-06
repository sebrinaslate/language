import streamlit as st
import genanki
import os
import tempfile
from gtts import gTTS

st.set_page_config(page_title="Flashcard Deck Generator", layout="centered")
st.title("🔊 TTS Flashcard Deck Generator")

st.markdown("""
Paste your vocab below, one pair per line:
```
french phrase,english translation
```
""")

text_input = st.text_area("Vocab Pairs", height=250, placeholder="Bonjour,Hello\nMerci,Thank you")
deck_name = st.text_input("Deck Name", "My TTS Deck")
deck_id = 1234567890  # You can randomize or hash this later

if st.button("Generate Deck"):
    if not text_input.strip():
        st.warning("Please paste some vocab pairs.")
    else:
        vocab = []
        for line in text_input.strip().split('\n'):
            if "," in line:
                french, english = line.strip().split(",", 1)
                vocab.append((french.strip(), english.strip()))

        model = genanki.Model(
            1607392319,
            'Simple TTS Model',
            fields=[
                {"name": "English"},
                {"name": "French"},
                {"name": "Audio"}
            ],
            templates=[{
                "name": "Card 1",
                "qfmt": "{{English}}",
                "afmt": "{{FrontSide}}<hr id='answer'>{{French}}{{Audio}}"
            }]
        )

        deck = genanki.Deck(deck_id, deck_name)

        with tempfile.TemporaryDirectory() as tmpdir:
            media_files = []
            for i, (french, english) in enumerate(vocab):
                filename = f"tts_{i}.mp3"
                filepath = os.path.join(tmpdir, filename)
                tts = gTTS(french, lang='fr')
                tts.save(filepath)
                media_files.append(filepath)
                note = genanki.Note(
                    model=model,
                    fields=[english, french, f"[sound:{filename}]"]
                )
                deck.add_note(note)

            output_path = os.path.join(tmpdir, "output_deck.apkg")
            genanki.Package(deck, media_files).write_to_file(output_path)

            with open(output_path, "rb") as f:
                st.success("✅ Your deck is ready!")
                st.download_button("📥 Download .apkg file", f, file_name="tts_deck.apkg")
