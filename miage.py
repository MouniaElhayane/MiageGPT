from flask import Flask, request, jsonify, render_template
import os
import requests
import sqlite3
import openai
import pyttsx3

# Initialiser l'application Flask
app = Flask(__name__)

# Set OpenAI key
openai.api_key = os.getenv('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')

# Connect to SQLite database
conn = sqlite3.connect('chat_history.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        user_message TEXT,
        bot_message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Configurer le moteur OpenAI
engine = "davinci-codex"  # Moteur GPT-3.5-turbo

# Configurer le synthétiseur vocal
engine_speech = pyttsx3.init()


# Fonction pour appeler l'API OpenAI
def call_openai_api(prompt):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=50  # Limitez le nombre de tokens générés à 50
    )
    return response.choices[0].text.strip()


# Gestion des commandes spéciales
def handle_special_commands(command):
    if command.startswith('/image'):
        # Appel à l'API DALL-E pour générer une image
        # Implémentez votre code pour interagir avec l'API DALL-E ici
        response = "Commande image : génération d'image avec DALL-E"
    elif command.startswith('/speech'):
        # Réponse vocalisée
        response = "Commande speech : réponse vocalisée"
        speech_output(response)
    elif command.startswith('/stable-diffusion'):
        # Utilisation des services de stable-diffusion
        response = "Commande stable-diffusion : utilisation des services de stable-diffusion"
    else:
        response = call_openai_api(command)

    return response


# Fonction pour synthétiser la réponse en voix
def speech_output(text):
    engine_speech.say(text)
    engine_speech.runAndWait()


# Route pour gérer les entrées de l'utilisateur
@app.route('/user-input', methods=['POST','GET'])
def handle_user_input():
    user_input = request.json['user_input']
    if user_input.startswith('/'):
        response = handle_special_commands(user_input)
    else:
        response = call_openai_api(user_input)
        # Stocker la question de l'utilisateur et la réponse du bot dans la base de données
        conn.execute('''
            INSERT INTO chat_history (user_message, bot_message) 
            VALUES (?, ?)
        ''', (user_input, response))
        conn.commit()
    return jsonify({'response': response})


@app.route('/')
def home():
    return render_template('chat.html')


if __name__ == '__main__':
    app.run(debug=True)
