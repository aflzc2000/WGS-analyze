#run_webui.py

import sys
import platform
import subprocess
import os
import streamlit as st

def main():

    system = platform.system()

    # 定义 Streamlit 命令
    if system == "Windows":
        command = [
            sys.executable, "-m", "streamlit", "run", ".\\Code\\blast_webui.py"
        ]
    else:
        command = [
            sys.executable, "-m", "streamlit", "run", "./Code/blast_webui.py"
        ]

    # 启动 Streamlit 应用
    subprocess.run(command)


if __name__ == "__main__":
    main()