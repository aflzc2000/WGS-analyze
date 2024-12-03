#!/bin/bash

# 获取当前脚本所在的目录
current_dir="$(cd "$(dirname "$0")" && pwd)"

# 目标目录：当前目录下的 Blast/macOS
target_dir="$current_dir/Blast/macOS"

# 临时添加 target_dir 到 PATH
export PATH="$target_dir:$PATH"

# 运行您的 Python 脚本
./Python/macOS/bin/python3 ./Code/run_webui.py