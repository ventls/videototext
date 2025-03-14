import os
from openai import OpenAI
import json

def process_txt_files(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 初始化OpenAI客户端
    client = OpenAI(api_key="<api_key>", base_url="https://api.deepseek.com")
    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            # 读取文本文件内容
            with open(input_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
                print(text_content)
            
            try:
                # 创建API请求
                response = client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[
                        {"role": "system", "content": "You are a human"},
                        {"role": "user", "content": (
                        	#f"这是一段A股午盘解析视频内容是: {text_content}，"
							#f"请纠正里面存在的股市用语的错误翻译，并且输出纠正后的内容，打印出来,最后另起一段总结这段内容"
							f"这是一段直播内容内容是: {text_content}，"
							f"因为是语音识别，可能存在一定的错误，请自行结合上下文纠正，并3000字左右总结里面的内容，如果内容较短不需要3000字"
                        )

                        },
                    ],
                    stream=True  # 启用流式输出
                )
                
                # 用于存储完整的响应内容
                full_response = ""
                
                # 处理流式响应
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        print(content, end='', flush=True)  # 实时打印到控制台
                        full_response += content
                
                print("\n")  # 每个文件处理完后换行
                
                # 将完整响应保存到输出文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_response)
                
                print(f"输出已保存: {filename}")
                
            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {str(e)}")

# 使用示例
input_directory = "./output3"
output_directory = "./summary"

process_txt_files(input_directory, output_directory)