from flask import Flask, request, Response, render_template_string
import requests
import os
import re

app = Flask(__name__)

# ======================================
OPENAI_API_KEY = "fk244398-QSw83MwkSHVOg8Sn1wyZBWHmBMA5EjMx"
OPENAI_BASE_URL = "https://openai.api2d.net/v1"
# Stable Diffusion API 配置
SD_API_KEY = "你的SD密钥"  # 可以用 Stability AI 或其他SD API
# ======================================

FRONTEND = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 全能助手</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
        .container{max-width:900px;margin:0 auto;background:white;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
        .header{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:25px;text-align:center}
        .tip{background:#e3f2fd;padding:15px;margin:15px;border-radius:10px;font-size:14px;color:#1565c0}
        .chat-box{height:500px;overflow-y:auto;padding:20px;background:#f8f9fa}
        .msg{margin-bottom:15px;padding:12px 16px;border-radius:18px;max-width:85%;line-height:1.6}
        .msg.user{background:linear-gradient(135deg,#667eea,#764ba2);color:white;margin-left:auto}
        .msg.ai{background:white;margin-right:auto;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
        .msg img{max-width:100%;border-radius:10px;margin-top:10px}
        .input-row{display:flex;gap:10px;padding:20px;border-top:1px solid #eee}
        input{flex:1;padding:12px 20px;border:2px solid #e5e5e5;border-radius:25px;font-size:15px;outline:none}
        button{padding:12px 30px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:25px;font-size:15px;font-weight:600;cursor:pointer}
        button:hover{transform:translateY(-2px)}
        .model-tag{display:inline-block;background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:10px;font-size:12px;margin-right:5px}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>🚀 AI 全能助手</h1></div>
        <div class="tip">
            <strong>💡 画图命令：</strong><br>
            <span class="model-tag">@draw</span> SD v1 模型<br>
            <span class="model-tag">@drawC</span> SD Core 模型<br>
            <span class="model-tag">@draw3</span> SD 3 模型<br>
            <span class="model-tag">@draw3t</span> SD 3 Turbo 模型<br>
            示例：@draw 一只可爱的猫咪
        </div>
        <div class="chat-box" id="chatBox">
            <div class="msg ai">你好！我是AI助手，输入 @draw + 描述 即可生成图片~</div>
        </div>
        <div class="input-row">
            <input id="chatInput" placeholder="输入问题，或 @draw + 描述 生成图片..." onkeypress="if(event.key=='Enter')send()">
            <button onclick="send()">发送</button>
        </div>
    </div>
    <script>
        async function send(){
            const v=document.getElementById('chatInput').value.trim();
            if(!v)return;
            document.getElementById('chatBox').innerHTML+='<div class="msg user">'+v+'</div>';
            document.getElementById('chatInput').value='';
            document.getElementById('chatBox').innerHTML+='<div class="msg ai">思考中...</div>';
            document.getElementById('chatBox').scrollTop=99999;
            
            const r=await fetch('/api/chat',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({msg:v})
            });
            const d=await r.json();
            document.getElementById('chatBox').lastChild.remove();
            
            let html = d.reply;
            if(d.image) {
                html += '<br><img src="'+d.image+'">';
            }
            document.getElementById('chatBox').innerHTML+='<div class="msg ai">'+html+'</div>';
            document.getElementById('chatBox').scrollTop=99999;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FRONTEND)

def generate_sd_image(prompt, model='sd3'):
    """Stable Diffusion 图片生成"""
    # 这里接入你的 Stable Diffusion API
    # 示例用 API2D 的 DALL-E，可替换为 Stability AI
    response = requests.post(
        f'{OPENAI_BASE_URL}/images/generations',
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
        json={'model': 'dall-e-3', 'prompt': prompt, 'n': 1, 'size': '1024x1024'}
    )
    result = response.json()
    if 'data' in result and result['data']:
        return result['data'][0]['url']
    return None

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    msg = data['msg']
    
    # 识别画图命令
    sd_patterns = {
        r'^@draw\s+': ('SD v1', 'sd1'),
        r'^@drawC\s+': ('SD Core', 'sd-core'),
        r'^@draw3\s+': ('SD 3', 'sd3'),
        r'^@draw3t\s+': ('SD 3 Turbo', 'sd3-turbo'),
    }
    
    for pattern, (model_name, model_id) in sd_patterns.items():
        match = re.match(pattern, msg, re.IGNORECASE)
        if match:
            prompt = msg[match.end():].strip()
            image_url = generate_sd_image(prompt, model_id)
            return {
                'reply': f'🎨 使用 {model_name} 生成图片完成！',
                'image': image_url
            }
    
    # 正常聊天
    response = requests.post(
        f'{OPENAI_BASE_URL}/chat/completions',
        json={'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': msg}]},
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'}
    )
    result = response.json()
    return {'reply': result['choices'][0]['message']['content']}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
