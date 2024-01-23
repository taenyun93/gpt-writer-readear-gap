from flask import Flask, render_template, request, redirect, url_for
#from openai import OpenAI
from openai import OpenAI
import os
from datetime import datetime, timezone
from dotenv import load_dotenv


# https://www.digitalocean.com/community/tutorials/how-to-use-templates-in-a-flask-application
load_dotenv()
api_key = os.environ["OPEN_API_KEY"]
client = OpenAI(
   api_key=api_key
)

InitialChat = "Hi, I am your AI Writing Assistant. How can I help you?"
chats = [InitialChat]
chat_log = []




#api_key="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"
#PID = 'R999999999'
# Set up Flask app
app = Flask(__name__)


# Allow embedding in iframes from any domain
#@app.after_request
#def add_header(response):
#    response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Allows embedding from all domains
#    return response

# Deifne home page route
@app.route('/<PID>', methods=['GET'])
def home(PID):


    assistant_id = "asst_svi4BeBWBwyU9ukAVbCOQs7F"
    #PID = request.args.get('PID', default = 'R999999999', type = str)
    thread = client.beta.threads.create()
    thread_id = thread.id

    return render_template('index.html',chats=chats,PID=PID,thread_id=thread_id,assistant_id=assistant_id,)


 # Define the Chatbot route

@app.route("/chatbot/<PID>/<assistant_id>/<thread_id>/<user_input>/<user_input_utc>", methods=['POST','GET'])
def chatbot(PID,assistant_id,thread_id,user_input,user_input_utc):
    #pass
    # Get the message input from users
    #PID = request.form["PID"]
    #thread_id = request.args.get('thread_id', default = 'R999999999', type = str)
    #if user_input == "NA":
    #    user_input = request.form["message"]
    #user_input_utc = datetime.now(timezone.utc)
    #Use the OpenAI API to generate a response
    #prompt = f"User: {}

    #PID = request.args.get('PID', default = 'R999999999', type = str)

    chatlog_txt = os.path.join("chatlog",str(PID) + "_" + str(thread_id) +".txt")

    message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content= user_input)

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id)#,
    #instructions="Please describe in two sentence")

    while True:
        run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run.id)
        if run.status != "in_progress" and run.status != "queued":
            break

    thread_messages = client.beta.threads.messages.list(thread_id)

    chats = [thread_message.content[0].text.value for thread_message in reversed(thread_messages.data)]

    chats.insert(0,InitialChat)

    chats = [chat.replace("\n", "<br>") for chat in chats]
    chat_log = [f"{thread_message.role}[{thread_messages.data[0].created_at}]: {thread_message.content[0].text.value}" for thread_message in reversed(thread_messages.data)]
    chat_log.insert(0,str(PID))
    #return render_template("chatbot.html")
    #chatlog_txt = str(PID) + ".txt"
    with open(chatlog_txt, 'w') as f:
        for line in chat_log:
            f.write(line)
            f.write('\n')
    return render_template(
    "chatbot.html",
    chats = chats,
    PID = PID,
    thread_id = thread_id,
    assistant_id = assistant_id,)


@app.route("/chatbotWait/<PID>/<assistant_id>/<thread_id>", methods=['POST','GET'])
def chatbotWait(PID,assistant_id,thread_id):
    #pass
    # Get the message input from users
    #PID = request.form["PID"]
    #thread_id = request.args.get('thread_id', default = 'R999999999', type = str)
    user_input = request.form["message"]
    user_input = user_input.replace("/","\\")
    user_input_utc = datetime.now(timezone.utc)
    #Use the OpenAI API to generate a response
    #prompt = f"User: {}


    thread_messages = client.beta.threads.messages.list(thread_id)

    chatsWait = [thread_message.content[0].text.value for thread_message in reversed(thread_messages.data)]

    chatsWait.insert(0,InitialChat)
    chatsWait = [chat.replace("\n", "<br>") for chat in chatsWait]
    chatsWait.append(user_input)


    return render_template(
    "chatbot_waiting.html",
    chats = chatsWait,
    PID = PID,
    thread_id = thread_id,
    assistant_id = assistant_id,
    user_input = user_input,
    user_input_utc=user_input_utc,)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
   #app.run('0.0.0.0', port=5000, debug=True,ssl_context=('cert.pem', 'key.pem'))
