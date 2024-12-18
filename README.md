# 细菌基因组序列分析软件整合包
本整合包整合微生物和细菌基因组分析领域常用的生物信息学软件，将软件命令行的指令通过可视化的浏览器界面展示和操作，无需任何代码即可一键安装和分析，并支持个性化参数配置，界面友好。软件使用纯python语言编写，支持跨平台。

### 平台支持：
软件可自动检测电脑运行的系统。已支持的平台：

**Windows：**

:green_circle: **WSL/WSL2：支持。** **推荐的运行方式*

:red_circle: **Powershell：部分支持。** **不推荐，除非软件conda全部使用noarch包，否则不能运行*

**Unix：**

:green_circle: **macOS：支持。**

:yellow_circle: **Linux：支持，但未经过测试。** **代码同macOS，理论可行*

### 软件功能：

本整合包目标是整合常用生物信息学软件。已实现的模块：

**Blast：**

引用NCBI的本地部署[Blast+](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html)程序，实现DNA序列的比对。软件特点：

1. 已集成全平台blastn和python二进制文件，并已添加环境变量，无需下载即可直接运行。
2. 本地运行，无需联网，速度快，可实现信息安全。
3. 针对cpu多线程优化，自动使用cpu全部线程数运行，提高速度。
4. 可自动查找全部平台的blast二进制文件，如果不想使用整合包中的，可自行选择本地的。
5. 支持输入多个查询序列和多个建库序列，任意数量实现依次比对。
6. 支持多种输出格式，包括常见格式1、6，以及合并表格输出。
7. 浏览器可视化界面，无需任何代码，界面简单易懂。

### 下载地址：

点击 **[Releases](https://github.com/aflzc2000/WGS-analyze/releases)** ，下载并解压 **software_v1.0.zip** 。

Windows用户双击 **“启动程序.bat”** 。

macOS或linux用户在该文件夹中打开终端，并输入 **“sh 启动程序.sh”** 。
