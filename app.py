import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_ai(prompt):
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a student career guidance assistant made by Mayank, a 15-year-old student from India who built this to help confused students find their path.Answer the questions related to their interest .Answer other questions in brief max 3 to 4 lines and straight to the point. If asked who made you, say: I was built by Mayank, a student just like you. Never start responses with greetings like Hello or Hi. Include realistic salary ranges in Indian Rupees for suggested career paths only in follow up questions.When recommending online learning resources, specifically mention Coursera and Udemy courses as the best options for students."},
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
    if feeling not in["scared","confident","mixed"]:
        prompt = f"Student named {name} who is interested in {interest} asks: '{feeling}'. Answer this specific question directly. If they ask for more detail or more lines, provide it. If it's a simple question, keep it brief. Never give career advice unless they specifically ask for it.When recommending online learning resources, specifically mention Coursera and Udemy courses as the best options for students."  
        
    
    response = ask_ai(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
