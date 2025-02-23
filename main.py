import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtCore import QTimer, QTime, Qt

class ShutdownApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('定时关机')
        self.setGeometry(300, 300, 300, 150)

        # 创建布局
        layout = QVBoxLayout()

        # 创建标签
        self.time_label = QLabel('请选择关机时间：', self)

        # 创建小时和分钟的下拉列表
        self.hour_combobox = QComboBox(self)
        self.minute_combobox = QComboBox(self)

        # 填充小时和分钟的选择框
        for i in range(24):
            self.hour_combobox.addItem(f"{i:02d}")
        for i in range(60):
            self.minute_combobox.addItem(f"{i:02d}")

        # 设置默认时间为当前时间
        current_time = QTime.currentTime()
        self.hour_combobox.setCurrentIndex(current_time.hour())
        self.minute_combobox.setCurrentIndex(current_time.minute())

        # 创建水平布局，用于显示小时和分钟
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hour_combobox)
        time_layout.addWidget(QLabel(" 时 "))
        time_layout.addWidget(self.minute_combobox)
        time_layout.addWidget(QLabel(" 分 "))

        # 创建设置按钮
        self.set_button = QPushButton('设置定时关机', self)
        self.set_button.clicked.connect(self.setShutdownTime)

        # 将控件添加到布局
        layout.addWidget(self.time_label)
        layout.addLayout(time_layout)  # 使用水平布局显示时间
        layout.addWidget(self.set_button)

        self.setLayout(layout)

        # 设置回车键响应
        self.set_button.setDefault(True)

        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkTime)

        self.shutdown_time = None

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 使用标准图标：获取计算机图标
        self.tray_icon.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))

        # 托盘菜单
        tray_menu = QMenu(self)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exitApp)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.trayIconActivated)
        self.tray_icon.setVisible(True)

    def keyPressEvent(self, event):
        """捕捉回车键事件，执行设置定时关机"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.setShutdownTime()  # 按下回车时触发设置关机时间

    def setShutdownTime(self):
        """获取用户选择的时间并计算与当前时间的差值"""
        hours = int(self.hour_combobox.currentText())
        minutes = int(self.minute_combobox.currentText())
        current_time = QTime.currentTime()
        shutdown_time = QTime(hours, minutes)

        # 如果设定时间已经过去，则将关机时间设为明天
        if current_time > shutdown_time:
            shutdown_time = shutdown_time.addSecs(24 * 3600)  # 明天的这个时间

        # 计算与当前时间的差值
        time_diff = current_time.msecsTo(shutdown_time) / 1000  # 转换为秒

        self.shutdown_time = time.time() + time_diff
        self.timer.start(1000)  # 每秒检查一次时间
        self.set_button.setEnabled(False)  # 禁用按钮
        self.hour_combobox.setEnabled(False)  # 禁用小时下拉框
        self.minute_combobox.setEnabled(False)  # 禁用分钟下拉框
        self.time_label.setText(f"定时关机设置为 {shutdown_time.toString('HH:mm')}，等待到达...")

    def checkTime(self):
        """检查当前时间是否已到达设定的关机时间"""
        if time.time() >= self.shutdown_time:
            self.timer.stop()
            self.time_label.setText("时间到！正在关机...")
            self.shutdown()

    def shutdown(self):
        """执行关机命令"""
        if sys.platform == "win32":
            os.system("shutdown /s /f /t 1")
        elif sys.platform == "linux" or sys.platform == "darwin":
            os.system("shutdown -h now")

    def trayIconActivated(self, reason):
        """托盘图标点击响应"""
        if reason == QSystemTrayIcon.Trigger:
            self.show()  # 点击托盘图标时恢复窗口

    def exitApp(self):
        """退出程序"""
        self.tray_icon.setVisible(False)
        QApplication.quit()

    def closeEvent(self, event):
        """重写关闭事件，点击×号时隐藏到托盘"""
        event.ignore()  # 忽略默认的关闭事件
        self.hide()  # 隐藏窗口
        self.tray_icon.showMessage("定时关机程序", "程序已最小化到托盘", QSystemTrayIcon.Information)

    def showEvent(self, event):
        """窗口显示时，居中显示"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()
        self.move((screen_geometry.width() - window_geometry.width()) // 2,
                  (screen_geometry.height() - window_geometry.height()) // 2)
        super().showEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShutdownApp()
    window.show()
    sys.exit(app.exec_())
