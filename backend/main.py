import subprocess
import os
import uuid
from faster_whisper import WhisperModel

# 配置参数
INPUT_DIR = "./video"             # 输入视频目录
OUTPUT_DIR = "./output"           # 输出文本目录
MODEL_SIZE = "medium"              # Whisper模型大小 # 可以换成"tiny", "base", "small", "medium"，"large"
BEAM_SIZE = 3                     # 束搜索大小
LANGUAGE = "zh"                   # 指定中文识别

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
    # 生成唯一临时文件名
    temp_audio = os.path.join(output_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
    
    try:
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_txt = os.path.join(output_dir, f"{base_name}.txt")

        # 步骤1: 用FFmpeg提取音频
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",                # 覆盖已有文件
            "-i", video_path,
            "-vn",               # 禁用视频流
            "-acodec", "pcm_s16le",
            "-ar", "16000",      # 采样率
            "-ac", "1",         # 单声道
            temp_audio
        ]
        
        # 运行FFmpeg
        subprocess.run(
            ffmpeg_cmd,
            check=True,
            stdout=subprocess.DEVNULL,  # 隐藏输出
            stderr=subprocess.DEVNULL
        )

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
                print(line.strip())
        return True

    except subprocess.CalledProcessError:
        print(f"FFmpeg处理失败: {os.path.basename(video_path)}")
        return False
    except Exception as e:
        print(f"识别异常: {os.path.basename(video_path)} - {str(e)}")
        return False
    finally:
        # 清理临时音频文件
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 初始化Whisper模型
    model = WhisperModel(
        MODEL_SIZE,
        device="cuda",
        compute_type="float16",
        download_root="./whisper-models"
    )

    # 获取待处理视频列表
    video_files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".mp4", ".mkv", ".ts"))
    ]

    print(f"发现 {len(video_files)} 个待处理视频")

    # 批量处理视频
    success_count = 0
    for idx, filename in enumerate(video_files, 1):
        video_path = os.path.join(INPUT_DIR, filename)
        print(f"\n[{idx}/{len(video_files)}] 正在处理: {filename}")
        
        if process_video(model, video_path, OUTPUT_DIR):
            success_count += 1
            print(f"✓ 处理成功: {filename}")
        else:
            print(f"× 处理失败: {filename}")

    print(f"\n处理完成！成功率: {success_count}/{len(video_files)}")

if __name__ == "__main__":
    main()