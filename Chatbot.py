import nltk
import spacy
import requests
from nltk.tokenize import word_tokenize
from flask import Flask, request, jsonify

# Download required NLTK data
nltk.download('punkt')

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# Global variable to maintain context
context = {}

# Example user data for personalization
user_data = {}

# Function to process input and recognize entities
def process_input(user_input):
    doc = nlp(user_input.lower())
    tokens = [token.text for token in doc]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return tokens, entities

# Function to get weather information
def get_weather(city):
    api_key = "936ddf4eb8fb977822931316b7066115"  
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temp}K."
    else:
        return "Sorry, I couldn't fetch the weather information."

# Function to generate chatbot responses
def chatbot_response(user_input, user_id):
    responses = {
        "hello": f"Hi there, {user_data.get(user_id, 'User')}! How can I help you today?",
        "bye": "Goodbye! Have a great day!",
        "how are you": "I'm a chatbot, I'm always good!",
        "default": "I'm sorry, I don't understand that.",
        "name": "My name is ChatBot. What's yours?",
        "weather": "I can provide weather updates. Which city are you interested in?"
    }
    
    user_tokens, user_entities = process_input(user_input)
    
    if user_id in context and context[user_id] == "name":
        context[user_id] = None
        user_data[user_id] = user_input
        return f"Nice to meet you, {user_input}!"
    elif user_id in context and context[user_id] == "weather":
        context[user_id] = None
        city = user_entities[0][0] if user_entities else user_input
        return get_weather(city)

    if "hello" in user_tokens:
        return responses["hello"]
    elif "bye" in user_tokens:
        return responses["bye"]
    elif "how" in user_tokens and "are" in user_tokens and "you" in user_tokens:
        return responses["how are you"]
    elif "name" in user_tokens:
        context[user_id] = "name"
        return responses["name"]
    elif "weather" in user_tokens:
        context[user_id] = "weather"
        return responses["weather"]
    else:
        return responses["default"]

# Flask route for chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    user_id = request.json.get('user_id', 'user1')
    response = chatbot_response(user_input, user_id)
    return jsonify({"response": response})

# Flask route for the web interface
@app.route('/')
def home():
    return '''
    <html>
        <body>
            <h1>Chatbot</h1>
            <input id="user_input" type="text">
            <button onclick="sendMessage()">Send</button>
            <div id="chat_log"></div>
            <script>
                function sendMessage() {
                    var user_input = document.getElementById("user_input").value;
                    fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: user_input, user_id: 'user1'}),
                    })
                    .then(response => response.json())
                    .then(data => {
                        var chat_log = document.getElementById("chat_log");
                        chat_log.innerHTML += "<p>You: " + user_input + "</p>";
                        chat_log.innerHTML += "<p>Bot: " + data.response + "</p>";
                    });
                }
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
