from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

LOCAL_LLM = os.getenv("LOCAL_LLM_URL", "http://192.168.35.251:8081/v1/chat/completions")

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    # Call local LLM
    try:
        response = requests.post(LOCAL_LLM, json={
            "model": "mistral",
            "messages": [{"role": "user", "content": user_message}],
            "max_tokens": 200
        })
        bot_reply = response.json()['choices'][0]['message']['content']
    except:
        bot_reply = "I'm learning. Try again later."
    
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run()
