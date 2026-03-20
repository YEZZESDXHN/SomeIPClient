import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from app.windows.main_window import MainWindow


def setup_logging():
    # 创建日志文件夹
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置 logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 定义格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # A. 文件处理器：保存到本地
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # # B. 控制台处理器：尝试连接到命令行
    # # 如果是打包后的 exe，且在命令行运行，sys.stdout 是存在的
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    return logger


# 初始化
log = setup_logging()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

# pyinstaller --onefile --windowed main.py
