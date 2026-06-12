from flask import Flask, request, Response, render_template_string
import requests
import os
import time

app = Flask(__name__)

# ======================================
# ✅ 配置你的密钥
OPENAI_API_KEY = "fk244398-QSw83MwkSHVOg8Sn1wyZBWHmBMA5EjMx"           # 聊天/画图用
RUNWAY_API_KEY = "你的Runway密钥"              # 视频生成用
OPENAI_BASE_URL = "https://openai.api2d.net/v1"
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
        .tabs{display:flex;background:#f5f5f5}
        .tab{flex:1;padding:15px;text-align:center;cursor:pointer;border:none;background:none;font-size:16px;font-weight:600;color:#666;transition:all 0.3s}
        .tab.active{background:white;color:#667eea;border-bottom:3px solid #667eea}
        .tab-content{display:none;padding:25px}
        .tab-content.active{display:block}
        .chat-box{height:450px;overflow-y:auto;padding:20px;background:#f8f9fa;border-radius:10px;margin-bottom:20px}
        .msg{margin-bottom:15px;padding:12px 16px;border-radius:18px;max-width:80%;line-height:1.6}
        .msg.user{background:linear-gradient(135deg,#667eea,#764ba2);color:white;margin-left:auto}
        .msg.ai{background:white;margin-right:auto;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
        .msg img,.msg video{max-width:100%;border-radius:10px;margin-top:10px}
        .input-row{display:flex;gap:10px;margin-bottom:10px}
        input,select{flex:1;padding:12px 20px;border:2px solid #e5e5e5;border-radius:25px;font-size:15px;outline:none}
        button{padding:12px 30px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:25px;font-size:15px;font-weight:600;cursor:pointer}
        button:hover{transform:translateY(-2px)}
        button:disabled{opacity:0.5}
        .image-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px;margin-top:20px}
        .card{border-radius:10px;overflow:hidden;box-shadow:0 3px 10px rgba(0,0,0,0.1)}
        .card img,.card video{width:100%;display:block}
        .loading{text-align:center;padding:40px;color:#666}
        .tip{background:#fff3cd;padding:15px;border-radius:10px;margin:15px 0}
        .progress{background:#e9ecef;height:8px;border-radius:4px;overflow:hidden;margin:10px 0}
        .progress-bar{background:linear-gradient(135deg,#667eea,#764ba2);height:100%;width:0%;transition:width 0.5s}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>🚀 AI 全能助手</h1><p style="opacity:0.9;margin-top:5px">聊天 | 画图 | 视频生成</p></div>
        
        <div class="tabs">
            <button class="tab active" onclick="tab('chat')">💬 聊天</button>
            <button class="tab" onclick="tab('image')">🎨 画图</button>
            <button class="tab" onclick="tab('video')">🎬 视频</button>
        </div>
        
        <div id="chat" class="tab-content active">
            <div class="chat-box" id="chatBox"><div class="msg ai">你好！我是AI助手，有什么可以帮助你的？</div></div>
            <div class="input-row"><input id="chatInput" placeholder="输入你的问题..." onkeypress="if(event.key=='Enter')sendChat()"><button onclick="sendChat()">发送</button></div>
        </div>
        
        <div id="image" class="tab-content">
            <h3 style="margin-bottom:15px">🎨 DALL-E AI 画图</h3>
            <div class="input-row">
                <input id="imgPrompt" value="一只可爱的猫咪在太空，赛博朋克风格">
                <select id="imgSize" style="flex:none;width:140px">
                    <option value="1024x1024">1024×1024</option>
                    <option value="512x512">512×512</option>
                </select>
                <button onclick="genImage()">生成图片</button>
            </div>
            <div id="imgResult"></div>
        </div>
        
        <div id="video" class="tab-content">
            <h3 style="margin-bottom:15px">🎬 Runway Gen-2 视频生成</h3>
            <div class="tip"><strong>💡 说明：</strong>生成视频约需1-3分钟，请耐心等待。</div>
            <div class="input-row">
                <input id="videoPrompt" value="一只小狗在草地上奔跑，阳光明媚，电影质感">
                <select id="videoDuration" style="flex:none;width:120px">
                    <option value="5">5秒</option>
                    <option value="10">10秒</option>
                </select>
                <button id="videoBtn" onclick="genVideo()">生成视频</button>
            </div>
            <div id="videoProgress" style="display:none">
                <div class="progress"><div class="progress-bar" id="progressBar"></div></div>
                <p style="text-align:center;color:#666" id="progressText">正在生成视频...</p>
            </div>
            <div id="videoResult"></div>
        </div>
    </div>
    <script>
        function tab(t){
            document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(t).classList.add('active');
        }
        async function sendChat(){
            const v=document.getElementById('chatInput').value.trim();
            if(!v)return;
            document.getElementById('chatBox').innerHTML+='<div class="msg user">'+v+'</div>';
            document.getElementById('chatInput').value='';
            document.getElementById('chatBox').innerHTML+='<div class="msg ai">思考中...</div>';
            document.getElementById('chatBox').scrollTop=99999;
            const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({msg:v})});
            const d=await r.json();
            document.getElementById('chatBox').lastChild.remove();
            document.getElementById('chatBox').innerHTML+='<div class="msg ai">'+d.reply+'</div>';
            document.getElementById('chatBox').scrollTop=99999;
        }
        async function genImage(){
            const p=document.getElementById('imgPrompt').value;
            const s=document.getElementById('imgSize').value;
            document.getElementById('imgResult').innerHTML='<div class="loading">🖌️ 正在生成图片...</div>';
            const r=await fetch('/api/image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p,size:s})});
            const d=await r.json();
            if(d.url){
                document.getElementById('imgResult').innerHTML='<div class="image-grid"><div class="card"><img src="'+d.url+'"></div></div>';
            }else{
                document.getElementById('imgResult').innerHTML='<p style="color:red">生成失败：'+JSON.stringify(d)+'</p>';
            }
        }
        async function genVideo(){
            const p=document.getElementById('videoPrompt').value;
            const btn=document.getElementById('videoBtn');
            btn.disabled=true;
            document.getElementById('videoProgress').style.display='block';
            document.getElementById('videoResult').innerHTML='';
            
            let progress=0;
            const timer=setInterval(()=>{
                progress+=5;
                if(progress>90) progress=90;
                document.getElementById('progressBar').style.width=progress+'%';
            },2000);
            
            const r=await fetch('/api/video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p})});
            const d=await r.json();
            
            clearInterval(timer);
            document.getElementById('progressBar').style.width='100%';
            document.getElementById('progressText').textContent='生成完成！';
            
            if(d.video){
                document.getElementById('videoResult').innerHTML='<div class="card"><video controls autoplay loop><source src="'+d.video+'" type="video/mp4"></video></div>';
            }else{
                document.getElementById('videoResult').innerHTML='<p style="color:red;margin-top:15px">'+(d.error||'生成失败，请检查Runway密钥')+'</p>';
            }
            btn.disabled=false;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FRONTEND)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    response = requests.post(
        f'{OPENAI_BASE_URL}/chat/completions',
        json={'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': data['msg']}]},
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'}
    )
    result = response.json()
    return {'reply': result['choices'][0]['message']['content']}

@app.route('/api/image', methods=['POST'])
def api_image():
    data = request.json
    response = requests.post(
        f'{OPENAI_BASE_URL}/images/generations',
        json={'model': 'dall-e-3', 'prompt': data['prompt'], 'n': 1, 'size': data['size']},
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'}
    )
    result = response.json()
    if 'data' in result and result['data']:
        return {'url': result['data'][0]['url']}
    return result

@app.route('/api/video', methods=['POST'])
def api_video():
    if not RUNWAY_API_KEY or RUNWAY_API_KEY == "你的Runway密钥":
        return {'error': '请先配置 Runway API 密钥'}
    
    data = request.json
    prompt = data['prompt']
    
    try:
        # 第一步：创建视频生成任务
        response = requests.post(
            'https://api.runwayml.com/v1/generate/text_to_video',
            headers={
                'Authorization': f'Bearer {RUNWAY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'duration': 5,
                'ratio': '16:9'
            }
        )
        
        task = response.json()
        
        if 'id' not in task:
            return {'error': task.get('message', '创建任务失败')}
        
        task_id = task['id']
        
        # 第二步：轮询等待生成完成（最多3分钟）
        for _ in range(60):
            time.sleep(3)
            status_response = requests.get(
                f'https://api.runwayml.com/v1/tasks/{task_id}',
                headers={'Authorization': f'Bearer {RUNWAY_API_KEY}'}
            )
            status = status_response.json()
            
            if status.get('status') == 'succeeded':
                video_url = status.get('output', [None])[0]
                return {'video': video_url}
            elif status.get('status') == 'failed':
                return {'error': '视频生成失败'}
        
        return {'error': '生成超时'}
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
