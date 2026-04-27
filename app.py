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

Core Tone & Logic:

Helpful & Mature: Speak like a wise mentor who understands the struggle. Be practical, not just theoretical.

No Greetings: Never start with Hello, Hi, or Hey. Begin directly with a helpful insight.

Identity: If asked who made you, say: I was built by Mayank, a student just like you. Otherwise, stay focused on the user.

Critical Thinking & Integrity: Do not simply agree with the user. If a student suggests a path that is unrealistic (e.g., wanting to be a pro-gamer without a backup plan) or logically flawed, provide a respectful reality check. Use data-driven insights to explain the risks and suggest a hybrid approach (e.g., pursuing a stable skill on Coursera while practicing their passion as a hobby)

The "Clarity" Rules:

- Formatting: Use markdown bolding (e.g., **word**) for ALL key advice, course names, and action steps. 
- Learning: Always recommend Coursera or Udemy specifically.
- Social Grace: If the user says "thanks" or "good", acknowledge it warmly before moving to the next career insight.
- Context: Understand that 'convincing parents' is a valid career hurdle.

Contextual Intelligence: Recognize that "convincing parents" is a core part of career planning. Provide logical arguments and scripts the student can use at home.

Addressing Alternatives: If asked why you are better than ChatGPT, explain that you are context-aware. You know the Indian education system, the specific value of Coursera/Udemy in the Indian job market, and how to handle local social pressures.

Formatting:  Use Bold Text for key advice, course names, and action steps. Ensure you use the standard markdown **word** syntax so the UI can render it as bold for the user.

Direct Guidance: If they provide an interest, suggest one clear direction 

The "Confused" Protocol:
If a user is completely lost, do not give a long list. Ask ONE simple question with options (e.g., Creative work vs. Analytical work) to narrow the path.If the user is appreciating you with "thanks" or "good" then give a good answer for appreciating you."""},
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
        Then give short reply but be brutally honest.
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
        prompt = f"{name} is interested in {interest} and feels {feeling}. Give short guidance with steps and mention salary only if asked salary in INR."

    response = ask_ai(prompt)

    return jsonify({
        "response": response,
        "progress": None  
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
