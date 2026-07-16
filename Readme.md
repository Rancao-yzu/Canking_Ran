# Canking_Ran on linux
Vector的Canking在主流平台上是有支持的，但是测试后发现，canking的驱动和Vector提供的驱动[Vector Canking Driver](https://www.kvaser.cn/single-download/?download_id=1017580)兼容性很差，即使连接kvaser，也会有channel识别问题。

其实，canking的功能是简单的，具体来说就三个功能（在连接单个Kvaser设备及其channel后）：
1. 发送can报文/循环发送/发送随机数据等（包括解析DBC后根据DBC变量进行发送），包含是否为拓展帧，是否为FD模式等。
2. 接收Can报文，包含解析Can格式，按照DBC解析变量值。
3. 筛选canid，查看can报文。


## 项目简介
Canking_Ran 是一个轻量级的 CAN 总线分析工具，专为 Kvaser CAN 接口卡设计。它提供了 Vector Canking 的核心功能，但在兼容性和易用性方面进行了优化。

操作系统：Linux、Python 版本：3.8+、硬件：Kvaser CAN 接口卡

```bash
# 安装 Python 依赖
pip install python-can cantools

# Linux 下需要安装 Kvaser 驱动
# 请访问 Kvaser 官网下载并安装 Linux 驱动
# https://www.kvaser.cn/single-download/?download_id=1017580
```

## 运行
```bash
cd Canking_Ran
python3 src/main.py

pyinstaller Canking_Ran.spec
# 输出位置：dist/Canking_Ran
```

----

```
Canking_Ran/
├── Resources/              
├── Readme.md
└── src/                    
    ├── main.py
    ├── gui_style.py
    ├── core/
    │   ├── __init__.py
    │   ├── can_bus.py
    │   └── dbc_loader.py
    ├── filter/
    │   ├── __init__.py
    │   └── can_filter.py
    ├── receiver/
    │   ├── __init__.py
    │   └── message_receiver.py
    ├── sender/
    │   ├── __init__.py
    │   └── message_sender.py
    └── ui/
        ├── __init__.py
        ├── config_panel.py
        ├── filter_panel.py
        ├── main_window.py
        ├── receive_panel.py
        └── send_panel.py
```