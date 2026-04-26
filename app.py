import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


user_progress = {}

def ask_ai(prompt):
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": """You are a thoughtful career guidance assistant for students, created by Mayank, a student from India. You understand that career choices in India are deeply tied to home pressures, family expectations, and financial stability.

Helpful & Mature. No greetings. Be practical.

Use **bold** for key advice.
Recommend Coursera/Udemy.

If unrealistic goal → give respectful reality check.

If confused → ask ONE simple question.

Keep answers clear, short, and useful."""},
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
    followup = data.get('followup', '')

    # Initialize user
    if name not in user_progress:
        user_progress[name] = {"day": 0, "active_plan": False}

    
    if followup and ("7 day" in followup.lower() or "7-day" in followup.lower()):
        user_progress[name]["day"] = 1
        user_progress[name]["active_plan"] = True

        prompt = f"""
        Create a **7-day action plan** for a student interested in {interest}.
        Keep it simple, beginner-friendly, and daily-based.
        """

        response = ask_ai(prompt)

        return jsonify({
            "response": response,
            "progress": 10
        })

    
    if user_progress[name]["active_plan"]:
        user_progress[name]["day"] += 1
        day = user_progress[name]["day"]

        if day > 10:
            day = 10

        progress = int((day / 10) * 100)

        prompt = f"""
        Student {name} is on **Day {day}** learning {interest}.

        First appreciate consistency.
        Then give short motivation.
        Then give 1-2 tasks.

        Keep it short.
        """

        response = ask_ai(prompt)

        return jsonify({
            "response": response,
            "progress": progress
        })

    
    if followup:
        prompt = f"{name} asks: {followup}"
    else:
        prompt = f"{name} is interested in {interest} and feels {feeling}. Give short guidance with steps and salary in INR."

    response = ask_ai(prompt)

    return jsonify({
        "response": response,
        "progress": None  
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
