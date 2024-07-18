import os

# 获取当前文件路径
current_path = os.path.abspath(__file__)
# 获取上级目录
parent_path = os.path.dirname(current_path)
# 获取上上级目录
file_path = os.path.dirname(parent_path)
