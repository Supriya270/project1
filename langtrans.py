import logging
import hashlib
from typing import Optional
from googletrans import Translator
from langdetect import detect, LangDetectException
from gtts import gTTS
import os

# ------------------------------
# Setup logging
# ------------------------------
logging.basicConfig(
    filename='langtrans.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ------------------------------
# Caching translations to avoid duplicates
# ------------------------------
class TranslationCache:
    def __init__(self):
        self.cache = {}

    def generate_key(self, text, src, dest):
        hash_input = f"{text}|{src}|{dest}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    def get(self, text, src, dest):
        key = self.generate_key(text, src, dest)
        return self.cache.get(key)

    def set(self, text, src, dest, translation):
        key = self.generate_key(text, src, dest)
        self.cache[key] = translation

# ------------------------------
# Language Translation Logic
# ------------------------------
class LanguageTranslator:
    def __init__(self):
        self.translator = Translator()
        self.cache = TranslationCache()

    def detect_language(self, text: str) -> Optional[str]:
        try:
            language = detect(text)
            logging.info(f"Detected language: {language}")
            return language
        except LangDetectException as e:
            logging.error(f"Error detecting language: {e}")
            return None

    def translate_text(self, text: str, src_lang: Optional[str], target_lang: str) -> str:
        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        src_lang = src_lang or self.detect_language(text)
        if not src_lang:
            raise ValueError("Could not detect source language.")

        cached_translation = self.cache.get(text, src_lang, target_lang)
        if cached_translation:
            logging.info(f"Returning cached translation for: {text}")
            return cached_translation

        try:
            result = self.translator.translate(text, src=src_lang, dest=target_lang)
            self.cache.set(text, src_lang, target_lang, result.text)
            logging.info(f"Translated from {src_lang} to {target_lang}: {result.text}")
            return result.text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            raise RuntimeError("Translation failed. Please try again.")

    def text_to_speech(self, text: str, lang: str, filename: str = "output.mp3") -> str:
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(filename)
            logging.info(f"Saved speech to file: {filename}")
            return filename
        except Exception as e:
            logging.error(f"TTS error: {e}")
            raise RuntimeError("Text-to-Speech conversion failed.")

# ------------------------------
# CLI Utility (for optional command-line testing)
# ------------------------------
def main():
    translator = LanguageTranslator()

    print("=== Language Translator CLI ===")
    text = input("Enter text to translate: ").strip()
    src = input("Enter source language (or leave blank for auto-detect): ").strip() or None
    dest = input("Enter target language (e.g., 'en' for English): ").strip()

    try:
        translated = translator.translate_text(text, src, dest)
        print(f"\nTranslated Text ({src or 'auto'} -> {dest}):\n{translated}\n")

        should_tts = input("Do you want to generate audio (y/n)? ").lower()
        if should_tts == 'y':
            filename = translator.text_to_speech(translated, dest)
            print(f"Audio saved to: {filename}")
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                else:
                    os.system(f"xdg-open {filename}")
            except Exception as e:
                logging.warning(f"Could not auto-play audio: {e}")

    except Exception as err:
        print(f"Error: {err}")

# ------------------------------
# For direct command-line use
# ------------------------------
if __name__ == "__main__":
    main()
