import os
import re
from opencc import OpenCC

def process_file(input_file, output_file):
    # 初始化繁体转简体转换器
    cc = OpenCC('t2s')
    
    # Read all lines from input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract timestamps and content
    chunks = []  # Store chunks of 10 lines with their timestamps
    current_chunk = []
    current_timestamps = []
    
    for line in lines:
        timestamp_match = re.match(r'\[(.*?)\]', line)
        if timestamp_match:
            current_timestamps.append(timestamp_match.group(1))
            # Get content after timestamp
            content_text = line[line.find(']')+1:].strip()
            if content_text:
                # 将内容转换为简体中文
                content_text = cc.convert(content_text)
                current_chunk.append(content_text)
                
            # When we have 10 lines, create a new chunk
            if len(current_chunk) == 10:
                first_ts = current_timestamps[0]
                last_ts = current_timestamps[-1]
                chunks.append(f"[{first_ts} -> {last_ts}]\n" + "\n".join(current_chunk))
                current_chunk = []
                current_timestamps = []
    
    # Handle remaining lines if any
    if current_chunk:
        first_ts = current_timestamps[0]
        last_ts = current_timestamps[-1]
        chunks.append(f"[{first_ts} -> {last_ts}]\n" + "\n".join(current_chunk))
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(chunks))
    
    print(f"处理完成: {input_file} -> {output_file}")

# Create output directory if it doesn't exist
if not os.path.exists('./output3'):
    os.makedirs('./output3')
    print("创建输出目录: ./output3")

# Process all txt files in output directory
file_count = 0
for filename in os.listdir('./output'):
    if filename.endswith('.txt'):
        file_count += 1
        input_path = os.path.join('./output', filename)
        output_path = os.path.join('./output3', filename)
        process_file(input_path, output_path)

print(f"\n处理完成! 总共处理了 {file_count} 个文件")
print(f"转换后的文件保存在 ./output3 目录下")