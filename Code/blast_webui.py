#blast_webui.py

import os
import subprocess
import tempfile
import csv
import zipfile
import streamlit as st
from contextlib import contextmanager
from system_detection import detect_blast_installations, windows_to_wsl_path, get_cpu_count

# 常量配置
output_formats = {"1": "6", "2": "1"}
cpu_threads = get_cpu_count()

@contextmanager
def temporary_directory():
    """上下文管理器：创建和清理临时目录"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

def save_uploaded_file(uploaded_file, dest_dir):
    """保存上传的文件到指定目录"""
    file_path = os.path.join(dest_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

def build_blast_db(db_files, temp_dir, command_prefix):
    """构建 BLAST 数据库"""
    db_names = []
    for db_file in db_files:
        db_name = os.path.splitext(db_file.name)[0]
        temp_db_file_path = save_uploaded_file(db_file, temp_dir)
        db_path = os.path.join(temp_dir, db_name)

        # 如果是 WSL 环境，转换 Windows 路径为 WSL 路径
        if command_prefix == ["wsl"]:
            temp_db_file_path = windows_to_wsl_path(temp_db_file_path)
            db_path = windows_to_wsl_path(db_path)

        cmd = command_prefix + ["makeblastdb", "-in", temp_db_file_path, "-dbtype", "nucl", "-out", db_path]
        subprocess.run(cmd, check=True)
        db_names.append(db_name)
    return db_names

def run_blast(query_path, db_name, temp_dir, output_format, threads, command_prefix):
    """运行 BLASTN"""
    output_file = os.path.join(temp_dir, f"{os.path.basename(query_path)}_{db_name}.txt")

    # 如果是 WSL 环境，转换 Windows 路径为 WSL 路径
    if command_prefix == ["wsl"]:
        query_path = windows_to_wsl_path(query_path)
        db_path = windows_to_wsl_path(os.path.join(temp_dir, db_name))
        output_file_wsl = windows_to_wsl_path(output_file)
    else:
        query_path = os.path.abspath(query_path)
        db_path = os.path.join(temp_dir, db_name)
        output_file_wsl = output_file  # Windows 路径保持不变

    # 生成输出文件路径（使用 WSL 路径用于 cmd 参数，但返回使用 Windows 路径）
    cmd = command_prefix + [
        "blastn",
        "-query", query_path,
        "-db", db_path,
        "-num_threads", str(threads),
        "-outfmt", output_format,
        "-out", output_file_wsl,  # 使用 WSL 格式路径
    ]
    subprocess.run(cmd, check=True)

    # 返回原始 Windows 路径的 output_file
    return output_file

def process_output(output_file, operation):
    """处理 BLAST 输出，返回特定格式数据"""
    results = []
    with open(output_file) as f:
        for line in f:
            cols = line.strip().split("\t")
            if operation == "3":
                results.append(cols[2])  # 匹配比例
            elif operation == "4":
                results.append(float(cols[4]) + float(cols[5]))  # 错配数和
    return results

def process_blast(fasta_files, db_files, operation, command_prefix):
    """主处理函数"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_files = []

        # 构建数据库
        db_names = build_blast_db(db_files, temp_dir, command_prefix)

        if operation in ["1", "2"]:
            # 生成单文件输出并压缩
            for fasta_file in fasta_files:
                query_path = save_uploaded_file(fasta_file, temp_dir)

                for db_name in db_names:
                    output_file = run_blast(
                        query_path, db_name, temp_dir,
                        output_formats[operation], cpu_threads, command_prefix
                    )
                    output_files.append(output_file)

            zip_file_path = os.path.join(temp_dir, "blast_outputs.zip")
            with zipfile.ZipFile(zip_file_path, "w") as zipf:
                for file_path in output_files:
                    zipf.write(file_path, arcname=os.path.basename(file_path))

            # 读取 ZIP 文件数据
            with open(zip_file_path, "rb") as f:
                zip_data = f.read()

            return [{'filename': 'blast_outputs.zip', 'data': zip_data, 'mime_type': 'application/zip'}]

        elif operation in ["3", "4"]:
            # 合并输出为多行多列表格
            table = {}
            headers = ["序列文件"] + db_names

            for fasta_file in fasta_files:
                query_path = save_uploaded_file(fasta_file, temp_dir)
                row = [os.path.basename(query_path)]

                for db_name in db_names:
                    output_file = run_blast(
                        query_path, db_name, temp_dir,
                        "6", cpu_threads, command_prefix
                    )
                    results = process_output(output_file, operation)
                    if results:
                        row.append(", ".join(map(str, results)))
                    else:
                        row.append("-")  # 如果没有匹配结果，填充为“-”

                table[os.path.basename(query_path)] = row

            csv_file_path = os.path.join(temp_dir, "blast_output_table.csv")
            with open(csv_file_path, "w", newline="") as csv_out:
                writer = csv.writer(csv_out)
                writer.writerow(headers)
                for row in table.values():
                    writer.writerow(row)

            # 读取 CSV 文件数据
            with open(csv_file_path, "rb") as f:
                csv_data = f.read()

            return [{'filename': 'blast_output_table.csv', 'data': csv_data, 'mime_type': 'text/csv'}]

# Streamlit 界面
def main():
    st.title("Blast比对程序")

    # 检测可用的 BLAST 安装
    installations = detect_blast_installations()

    if not installations:
        st.error("未检测到 BLAST 程序，请前往https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/下载。")
        return

    # 准备供选择的选项
    options = [f"{inst['platform']}-v{inst['version']}" for inst in installations]

    # 初始化会话状态中的 selected_installation
    if 'selected_installation' not in st.session_state:
        st.session_state['selected_installation'] = installations[0]  # 默认选择第一个

    # 在顶部添加选择框
    selected_option = st.selectbox("请选择已检测到的blast程序：", options)

    # 根据用户选择的选项获取对应的安装信息
    selected_installation = next(
        (inst for inst in installations if f"{inst['platform']}-v{inst['version']}" == selected_option),
        None
    )

    # 将选择的安装信息存储到会话状态
    st.session_state['selected_installation'] = selected_installation

    # 用户上传文件
    uploaded_fasta_files = st.file_uploader("请选择查询序列", accept_multiple_files=True, type=["fasta", "seq"])
    uploaded_db_files = st.file_uploader("请选择建库序列", accept_multiple_files=True, type=["fasta", "seq"])

    # 选择操作
    operation = st.selectbox(
        "请选择输出格式：",
        [
            "每个文件单独输出-简略(格式6)-txt",
            "每个文件单独输出-详细(格式1)-txt",
            "合并为表格输出-匹配比例(格式6第3列)-csv",
            "合并为表格输出-错配数(格式6第5、6列)-csv",
        ],
        index=None
    )

    # 按钮触发处理
    if uploaded_fasta_files and uploaded_db_files and operation:
        if st.button("开始分析"):
            try:
                st.markdown(f"使用的cpu线程数：{cpu_threads}")

                operation_code = {
                    "每个文件单独输出-简略(格式6)-txt": "1",
                    "每个文件单独输出-详细(格式1)-txt": "2",
                    "合并为表格输出-匹配比例(格式6第3列)-csv": "3",
                    "合并为表格输出-错配数(格式6第5、6列)-csv": "4",
                }.get(operation)

                # 获取所选安装的命令前缀
                command_prefix = selected_installation['command_prefix']

                output_files = process_blast(uploaded_fasta_files, uploaded_db_files, operation_code, command_prefix)

                for output_file in output_files:
                    st.download_button(
                        label=f"下载 {output_file['filename']}",
                        data=output_file['data'],
                        file_name=output_file['filename'],
                        mime=output_file['mime_type']
                    )
            except Exception as e:
                st.error(f"分析失败：{str(e)}")

if __name__ == "__main__":
    main()
