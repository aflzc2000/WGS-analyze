#system_detection.py

import platform
import subprocess
import os

def detect_blast_installations():
    """检测系统中可用的 BLAST 安装，并返回其信息列表。"""
    installations = []

    system = platform.system()

    if system == "Windows":
        # 检查在 Powershell 中是否安装了 BLAST
        try:
            # 在 Powershell 中运行 'blastn -version'
            result = subprocess.run(
                ["blastn", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            version = parse_blast_version(result.stdout)
            installations.append({
                'platform': 'Windows-Powershell',
                'command_prefix': [],  # 不需要前缀
                'version': version
            })
        except Exception:
            pass  # Powershell 中未找到 BLAST

        # 检查在 WSL2 中是否安装了 BLAST
        try:
            # 运行 'wsl blastn -version'
            result = subprocess.run(
                ["wsl", "blastn", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            version = parse_blast_version(result.stdout)
            installations.append({
                'platform': 'Windows-WSL2',
                'command_prefix': ["wsl"],  # 使用 'wsl' 作为前缀
                'version': version
            })
        except Exception:
            pass  # WSL2 中未找到 BLAST 或未安装 WSL2

    elif system == "Darwin" or system == "Linux":
        # 对于 macOS（Darwin）和 Linux
        try:
            # 运行 'blastn -version'
            result = subprocess.run(
                ["blastn", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            version = parse_blast_version(result.stdout)
            installations.append({
                'platform': f"{system}-bash",
                'command_prefix': [],  # 不需要前缀
                'version': version
            })
        except Exception:
            pass  # 未找到 BLAST

    return installations

def parse_blast_version(version_output):
    """从 BLAST 的版本输出中解析版本号。"""
    # 示例输出: 'blastn: 2.9.0+\nPackage: ...'
    lines = version_output.strip().split('\n')
    if lines:
        first_line = lines[0]
        if ':' in first_line:
            version = first_line.split(':')[1].strip()
            return version
    return 'Unknown'

def windows_to_wsl_path(windows_path):
    """将 Windows 路径转换为 WSL 格式路径"""
    # 将反斜杠换为斜杠，并且转换 C: 为 /mnt/c/
    wsl_path = windows_path.replace("C:\\", "/mnt/c/").replace("\\", "/")
    return wsl_path

def get_cpu_count():
    try:
        cpu_count = os.cpu_count()
        if cpu_count is None:
            raise ValueError("无法检测到 CPU 核心数")
        return cpu_count
    except Exception as e:
        print(f"检测 CPU 核心数时出错: {e}")
        return 1  # 默认使用单线程