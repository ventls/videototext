import subprocess
import os
import uuid
from faster_whisper import WhisperModel
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import time
import queue
import threading
import json

app = Flask(__name__)
CORS(app)

# 配置参数
INPUT_DIR = "./videos"             # 输入视频目录
OUTPUT_DIR = "./output"           # 输出文本目录
MODEL_SIZE = "medium"              # Whisper模型大小
BEAM_SIZE = 3                     # 束搜索大小
LANGUAGE = "zh"                   # 指定中文识别

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 创建一个消息队列用于SSE
message_queue = queue.Queue()

def send_message(message, message_type='message'):
    """发送消息到队列"""
    try:
        message_queue.put({"message": message, "type": message_type}, timeout=1)
    except queue.Full:
        pass  # 如果队列满了，跳过这条消息

def format_duration(seconds_float):
    """将秒数格式化为易读的时间字符串"""
    seconds = seconds_float
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60

    if hours > 0:
        return f"{hours}h {minutes:02}m {seconds:05.2f}s"
    elif minutes > 0:
        return f"{minutes}m {seconds:05.2f}s"
    else:
        return f"{seconds:.2f}s"

def process_video(model, video_path, output_dir):
    """处理单个视频文件"""
    temp_audio = os.path.join(output_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
    
    try:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_txt = os.path.join(output_dir, f"{base_name}.txt")

        send_message("开始处理视频...", "status")
        
        # 步骤1: 用FFmpeg提取音频
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            temp_audio
        ]
        
        send_message("正在提取音频...", "status")
        subprocess.run(
            ffmpeg_cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        send_message("开始语音识别...", "status")
        # 步骤2: 执行语音识别
        segments, _ = model.transcribe(
            temp_audio,
            beam_size=BEAM_SIZE,
            language=LANGUAGE,
            vad_filter=True,
            initial_prompt="以下是普通话的句子。"
        )

        # 步骤3: 写入文本文件
        with open(output_txt, "w", encoding="utf-8") as f:
            for segment in segments:
                start_time = format_duration(segment.start)
                end_time = format_duration(segment.end)
                line = f"[{start_time} -> {end_time}] {segment.text}\n"
                f.write(line)
                send_message(line.strip())
                time.sleep(0.1)  # 添加小延迟使输出更平滑
        
        send_message("处理完成！", "status")
        return True

    except subprocess.CalledProcessError:
        send_message(f"FFmpeg处理失败: {os.path.basename(video_path)}", "error")
        return False
    except Exception as e:
        send_message(f"识别异常: {os.path.basename(video_path)} - {str(e)}", "error")
        return False
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = file.filename
        file_path = os.path.join(INPUT_DIR, filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "filename": filename})

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    
    video_path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(video_path):
        return jsonify({"error": "File not found"}), 404
    
    # 初始化Whisper模型
    try:
        send_message("正在加载模型...", "status")
        model = WhisperModel(
            MODEL_SIZE,
            device="cuda",  # 使用CUDA
            compute_type="float16",  # 使用float16以提高性能
            download_root="./whisper-models"
        )
        send_message("模型加载完成", "status")
    except Exception as e:
        send_message(f"模型加载失败: {str(e)}", "error")
        return jsonify({"error": "Model loading failed"}), 500
    
    # 在新线程中处理视频
    thread = threading.Thread(target=process_video, args=(model, video_path, OUTPUT_DIR))
    thread.daemon = True  # 设置为守护线程
    thread.start()
    return jsonify({"message": "Conversion started"})

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                message = message_queue.get(timeout=30)  # 30秒超时
                yield f"data: {json.dumps(message)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'message': 'keep-alive', 'type': 'ping'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/output/<filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)  # 禁用重载器以防止重复启动