from flask import Flask, request, render_template, session
import openai
import pickle
import os

# Initialize Flask, OpenAI, and session management
app = Flask(__name__)
app.secret_key=os.urandom(24)

API_KEY = 'sk-proj-ObCXSsQk6oiBdPEyjuKFT3BlbkFJsN74caZoHBLCb6vsidR6'
openai.api_key = API_KEY
model_id = 'gpt-3.5-turbo'

model = pickle.load(open('PCASSS_model.pkl', 'rb'))

def get_gpt_response(conversation):
    """Handles conversation with GPT by adding the new user message and retrieving GPT's response."""
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation
    )
    conversation.append({'role': 'system', 'content': response.choices[0].message.content})
    return conversation

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inspect", methods=["GET", "POST"])
def inspect():
    if request.method == "POST":
        data = [float(request.form[key]) for key in ['GlobalReactivePower', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']]
        prediction = str(round(model.predict([data])[0], 3))
        session['conversation'] = [{'role': 'system', 'content': f"Based on your input, the predicted energy consumption is {prediction} watts. You can ask me anything about this prediction."}]
        return render_template("output.html", conversation=session['conversation'])
    return render_template("inspect.html")

@app.route("/output", methods=["GET", "POST"])
def output():
    conversation = session.get('conversation', [])
    if request.method == "POST":
        user_message = request.form['message']
        conversation.append({'role': 'user', 'content': user_message})
        conversation = get_gpt_response(conversation)
        session['conversation'] = conversation
    return render_template("output.html", conversation=conversation)

if __name__ == "__main__":
    app.run(debug=True)