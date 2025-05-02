from flask import Flask, render_template, request, url_for
from langtrans import LanguageTranslator
import os

app = Flask(__name__)
translator = LanguageTranslator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    original_text = request.form['text']
    source_lang = request.form.get('source_lang') or None
    target_lang = request.form['target_language'] 
    
    try:
        translated_text = translator.translate_text(original_text, source_lang, target_lang)

        # Generate speech file
        audio_filename = "output.mp3"
        filepath = os.path.join("static", audio_filename)
        translator.text_to_speech(translated_text, target_lang, filepath)

        return render_template('result.html',
                               original=original_text,
                               translated=translated_text,
                               audio_file=audio_filename)
    except Exception as e:
        return render_template('index.html', original_text=original_text,
                               translated_text=f"Error: {e}", target_language=target_lang)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
