import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_ai(prompt):
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a student career guidance assistant made by Mayank. Only answer questions related to careers, skills, and future paths. Never start with greetings. Include salary ranges in Indian Rupees."},
            {"role": "user", "content": prompt}
        ]
    )
    return chat.choices[0].message.content

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/guide', methods=['POST'])
def guide():
    data = request.json
    name = data.get('name', 'Student')
    interest = data.get('interest', '')
    feeling = data.get('feeling', 'mixed')
    prompt = f"A student named {name} is interested in {interest} and feeling {feeling} about their future. Give specific friendly career guidance with exact next steps and salary ranges in Indian Rupees. Max 6 lines."
    response = ask_ai(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
