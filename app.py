import streamlit as st
import genanki
import os
import tempfile
from gtts import gTTS

# === PAGE SETUP ===
st.set_page_config(page_title="Anki Deck Generator", page_icon="🗣️")
st.markdown("""
    <style>
        .stApp {
            max-width: 800px;
            margin: auto;
            padding: 2rem;
        }
        h1, h2 {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🗣️ French Audio Flashcard Generator")
st.caption("Paste your vocab list and generate a downloadable Anki deck with native French audio.")

# === INPUT SECTION ===
st.header("📋 1. Enter Your Vocabulary")
vocab_text = st.text_area("Each line should be: French word, English meaning", height=250)
deck_name = st.text_input("📝 Name your deck (optional):", value="MyFrenchDeck")

# === DECK GENERATION ===
st.header("⚙️ 2. Generate Your Anki Deck")
if st.button("🎧 Create Anki Deck"):
    if not vocab_text.strip():
        st.warning("Please paste some vocabulary.")
    else:
        # Process vocab
        vocab_lines = [line.strip() for line in vocab_text.strip().splitlines() if "," in line]
        vocab = [tuple(map(str.strip, line.split(",", 1))) for line in vocab_lines]

        # Set up temp dir for mp3s
        temp_dir = tempfile.TemporaryDirectory()
        media_files = []
        notes = []

        # Anki deck + model
        deck_id = abs(hash(deck_name)) % (10 ** 10)
        model = genanki.Model(
            1607392319,
            "French TTS Model",
            fields=[{"name": "English"}, {"name": "French"}, {"name": "Audio"}],
            templates=[{
                "name": "Card 1",
                "qfmt": "{{English}}",
                "afmt": "{{FrontSide}}<hr id='answer'>{{French}}<br>{{Audio}}"
            }]
        )
        deck = genanki.Deck(deck_id, deck_name)

        # Generate TTS & cards
        for french, english in vocab:
            filename = f"{french.replace(' ', '_')}.mp3"
            path = os.path.join(temp_dir.name, filename)
            tts = gTTS(text=french, lang='fr')
            tts.save(path)
            media_files.append(path)
            note = genanki.Note(
                model=model,
                fields=[english, french, f"[sound:{filename}]"]
            )
            deck.add_note(note)

        # Export deck
        output_path = os.path.join(temp_dir.name, f"{deck_name}.apkg")
        genanki.Package(deck, media_files).write_to_file(output_path)

        st.success("✅ Done! Your deck is ready to download.")
        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Download Anki Deck",
                data=f,
                file_name=f"{deck_name}.apkg",
                mime="application/octet-stream"
            )

# === FOOTER ===
st.markdown("---")
st.markdown("Made with 💖 by Sebrina (https://github.com/sebrinaslate)")
