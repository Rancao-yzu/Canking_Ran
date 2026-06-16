# Canking_Ran on linux
Vector的Canking在主流里怒下平台上是有支持的，但是测试后发现，canking的驱动和Vector提供的驱动[Vector Canking Driver](https://www.kvaser.cn/single-download/?download_id=1017580)兼容性很差，即使连接kvaser，也会有channel识别问题。

其实，canking的功能是简单的，具体来说就三个功能（在连接单个Kvaser设备及其channel后）：
1. 发送can报文/循环发送/发送随机数据等（包括解析DBC后根据DBC变量进行发送），包含是否为拓展帧，是否为FD模式等。
2. 接收Can报文，包含解析Can格式，按照DBC解析变量值。
3. 筛选canid，查看can报文。
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