from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# ======================================
OPENAI_API_KEY = "fk244398-QSw83MwkSHVOg8Sn1wyZBWHmBMA5EjMx"
OPENAI_BASE_URL = "https://openai.api2d.net/v1"
# ======================================

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <title>AI 助手</title>
    <style>
        body{font-family:Arial;max-width:800px;margin:0 auto;padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}
        .box{background:white;border-radius:15px;padding:20px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}
        h1{text-align:center;color:#667eea}
        #chat{height:400px;overflow-y:auto;padding:15px;background:#f8f9fa;border-radius:10px;margin-bottom:15px}
        .msg{margin-bottom:12px;padding:10px 14px;border-radius:15px;max-width:80%}
        .user{background:#667eea;color:white;margin-left:auto}
        .ai{background:#e9ecef;margin-right:auto}
        .row{display:flex;gap:10px}
        input{flex:1;padding:12px 18px;border:2px solid #e5e5e5;border-radius:25px;outline:none}
        button{padding:12px 25px;background:#667eea;color:white;border:none;border-radius:25px;cursor:pointer}
    </style>
</head>
<body>
    <div class="box">
        <h1>🤖 AI 智能助手</h1>
        <div id="chat"><div class="msg ai">你好！有什么可以帮助你的？</div></div>
        <div class="row">
            <input id="input" placeholder="输入问题..." onkeypress="if(event.key=='Enter')send()">
            <button onclick="send()">发送</button>
        </div>
    </div>
    <script>
        async function send(){
            const v = document.getElementById('input').value.trim();
            if(!v) return;
            document.getElementById('chat').innerHTML += '<div class="msg user">'+v+'</div>';
            document.getElementById('input').value='';
            document.getElementById('chat').innerHTML += '<div class="msg ai">思考中...</div>';
            const r = await fetch('/chat',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({msg:v})
            });
            const data = await r.json();
            document.getElementById('chat').lastChild.remove();
            document.getElementById('chat').innerHTML += '<div class="msg ai">'+data.reply+'</div>';
            document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
        }
    </script>
</body>
</html>
    """

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = requests.post(
        f'{OPENAI_BASE_URL}/chat/completions',
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': data['msg']}]
        },
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'}
    )
    result = response.json()
    return {'reply': result['choices'][0]['message']['content']}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)