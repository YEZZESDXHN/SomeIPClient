import json
import os
import socket
import struct
import sys
from time import sleep
from typing import Union, Optional

from PySide6.QtCore import Slot, QThread, QObject, Signal, QTimer, Qt
from PySide6.QtGui import QStandardItemModel, QAction, QCursor, QStandardItem
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableView, QMenu
from scapy.all import conf
from scapy.contrib.automotive.someip import SDEntry_Service, SDOption_IP4_EndPoint, SD, SOMEIP, SDEntry_EventGroup
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether, Dot1Q
from scapy.sendrecv import sendp

from app.resources.resources import IconEngine
from app.ui.MainWindow import Ui_MainWindow


def get_multicast_mac(ip):
    if not ip.startswith("224."):
        return "ff:ff:ff:ff:ff:ff"
    ip_bytes = struct.unpack("!I", socket.inet_aton(ip))[0]
    mac_num = 0x01005E000000 | (ip_bytes & 0x7FFFFF)
    return ":".join([f"{(mac_num >> i) & 0xFF:02x}" for i in (40, 32, 24, 16, 8, 0)])



class SomeIPSender:
    def __init__(self):
        self.iface = None
        self.sd_session_id = 0
        self.someip_session_id = 0

    def send_someip(self,
                    vlan_id: Optional[int],
                    s_mac,
                    d_mac,
                    s_ip,
                    d_ip,
                    srv_id,
                    method_id,
                    client_id,
                    msg_type,
                    payload,
                    sport,
                    dport):
        u = UDP(sport=sport, dport=dport)
        i = IP(src=s_ip, dst=d_ip)  # IP可保留，二层发送不影响上层
        sip = SOMEIP()
        sip.iface_ver = 1
        sip.proto_ver = 1
        sip.msg_type = msg_type  # "REQUEST"
        sip.retcode = "E_OK"
        self.someip_session_id += 1
        sip.session_id = self.someip_session_id
        sip.srv_id = srv_id
        sip.client_id = client_id
        sip.sub_id = method_id
        sip.add_payload(payload)

        ether = Ether(src=s_mac, dst=d_mac)
        if vlan_id:
            vlan_tag = Dot1Q(vlan=vlan_id)
            p = ether / vlan_tag/ i / u / sip
        else:
            p = ether / i / u / sip

        sendp(p, iface=self.iface, verbose=0)

    def send_someip_sd(self,
                       vlan_id: Optional[int],
                       s_mac,
                       d_mac,
                       s_ip,
                       d_ip,
                       sd_entry: Union[SDEntry_Service, SDEntry_EventGroup],
                       sd_option_ip4_end_point: SDOption_IP4_EndPoint = None,
                       sport=30490,
                       dport=30490):
        u = UDP(sport=sport, dport=dport)
        i = IP(src=s_ip, dst=d_ip)

        # ea = SDEntry_Service()
        #
        # ea.type = 0x01
        # ea.srv_id = 0x1234
        # ea.inst_id = 0x5678
        # ea.major_ver = 0x00
        # ea.index_1 = 0
        # ea.n_opt_1 = 1
        # ea.ttl = 3
        #
        # oa = SDOption_IP4_EndPoint()
        # oa.addr = "192.168.0.13"
        # oa.l4_proto = 0x11
        # oa.port = 30509

        sd = SD()
        sd.flags = 0xc0
        sd.set_entryArray(sd_entry)
        sd.set_optionArray(sd_option_ip4_end_point)

        ether = Ether(src=s_mac, dst=d_mac)

        if vlan_id:
            vlan_tag = Dot1Q(vlan=vlan_id)
            p = ether / vlan_tag / i / u / SOMEIP() / sd
        else:
            p = ether / i / u / SOMEIP() / sd
        p[SOMEIP].session_id = self.sd_session_id
        sendp(p, iface=self.iface, verbose=0)


class ZCUSomeipSender(QObject, SomeIPSender):
    def __init__(self, parent: "MainWindow"=None):
        super().__init__(parent)
        self.parent = parent

    def send_multicast_usage_mode(self, usage_mode: int):
        self.sd_session_id += 1
        s32g_ip = '172.16.114.10'
        multicast_ip = self.parent.comboBox_multicast.currentText()
        s32g_mac = '02:DF:53:00:00:00'
        multicast_mac = get_multicast_mac(multicast_ip)

        zcul_ip = '172.16.114.60'
        zcul_mac = '02:DF:53:00:00:20'
        zcur_ip = '172.16.114.70'
        zcur_mac = '02:DF:53:00:00:30'

        sd_entry_service = SDEntry_Service()
        sd_entry_service.type = 1
        sd_entry_service.n_opt_1 = 1
        sd_entry_service.srv_id = 0x4000
        sd_entry_service.inst_id = 1
        sd_entry_service.major_ver = 1
        sd_entry_service.minor_ver = 1
        sd_entry_service.ttl = 5

        sd_option_ip4_end_point = SDOption_IP4_EndPoint()
        sd_option_ip4_end_point.type = 4
        sd_option_ip4_end_point.addr = s32g_ip
        sd_option_ip4_end_point.l4_proto = 17
        sd_option_ip4_end_point.port = 50102

        # offer
        self.send_someip_sd(vlan_id=14,
                            s_mac=s32g_mac,
                            d_mac=multicast_mac,
                            s_ip=s32g_ip,
                            d_ip=multicast_ip,
                            sd_entry=sd_entry_service,
                            sd_option_ip4_end_point=sd_option_ip4_end_point)

        sleep(0.2)
        # ack

        sd_entry_event_group = SDEntry_EventGroup()
        sd_entry_event_group.type = 7
        sd_entry_event_group.index_1 = 0
        sd_entry_event_group.index_2 = 0
        sd_entry_event_group.n_opt_1 = 0
        sd_entry_event_group.n_opt_2 = 0
        sd_entry_event_group.srv_id = 0x4000
        sd_entry_event_group.inst_id = 1
        sd_entry_event_group.major_ver = 1
        sd_entry_event_group.ttl = 5
        sd_entry_event_group.eventgroup_id = 0x4000
        self.send_someip_sd(vlan_id=14,
                            s_mac=s32g_mac,
                            d_mac=multicast_mac,
                            # d_mac=zcul_mac,
                            s_ip=s32g_ip,
                            d_ip=multicast_ip,
                            # d_ip=zcul_ip,
                            sd_entry=sd_entry_event_group,
                            sd_option_ip4_end_point=[])

        sleep(0.2)
        # usage mode
        self.send_someip(vlan_id=14,
                         s_mac=s32g_mac,
                         d_mac=multicast_mac,
                         s_ip=s32g_ip,
                         d_ip=multicast_ip,
                         srv_id=0x4000,
                         method_id=0x8001,
                         client_id=0x60,
                         msg_type=2,
                         payload=usage_mode.to_bytes(1, "big"),
                         sport=50102,
                         dport=1024)

    def send_ml_fuse_id_on(self, fuse_id):
        s32g_ip = '172.16.114.10'
        zcu_ip = '172.16.114.60'
        s32g_mac = '02:DF:53:00:00:00'
        zcu_mac = '02:DF:53:00:00:20'

        self.send_someip(vlan_id=14,
                         s_mac=s32g_mac,
                         d_mac=zcu_mac,
                         s_ip=s32g_ip,
                         d_ip=zcu_ip,
                         srv_id=0x6002,
                         method_id=0x0001,
                         client_id=0x60,
                         msg_type=0,
                         payload=fuse_id.to_bytes(2, "big"),
                         sport=56001,
                         dport=56001)

    def send_ml_fuse_id_off(self, fuse_id):
        s32g_ip = '172.16.114.10'
        zcu_ip = '172.16.114.60'
        s32g_mac = '02:DF:53:00:00:00'
        zcu_mac = '02:DF:53:00:00:20'

        self.send_someip(vlan_id=14,
                         s_mac=s32g_mac,
                         d_mac=zcu_mac,
                         s_ip=s32g_ip,
                         d_ip=zcu_ip,
                         srv_id=0x6002,
                         method_id=0x0002,
                         client_id=0x60,
                         msg_type=0,
                         payload=fuse_id.to_bytes(2, "big"),
                         sport=56001,
                         dport=56001)

    def send_mr_fuse_id_on(self, fuse_id):
        s32g_ip = '172.16.114.10'
        zcu_ip = '172.16.114.70'
        s32g_mac = '02:DF:53:00:00:00'
        zcu_mac = '02:DF:53:00:00:30'

        self.send_someip(vlan_id=14,
                         s_mac=s32g_mac,
                         d_mac=zcu_mac,
                         s_ip=s32g_ip,
                         d_ip=zcu_ip,
                         srv_id=0x6003,
                         method_id=0x0001,
                         client_id=0x60,
                         msg_type=0,
                         payload=fuse_id.to_bytes(2, "big"),
                         sport=56002,
                         dport=56002)

    def send_mr_fuse_id_off(self, fuse_id):
        s32g_ip = '172.16.114.10'
        zcu_ip = '172.16.114.70'
        s32g_mac = '02:DF:53:00:00:00'
        zcu_mac = '02:DF:53:00:00:30'

        self.send_someip(vlan_id=14,
                         s_mac=s32g_mac,
                         d_mac=zcu_mac,
                         s_ip=s32g_ip,
                         d_ip=zcu_ip,
                         srv_id=0x6003,
                         method_id=0x0002,
                         client_id=0x60,
                         msg_type=0,
                         payload=fuse_id.to_bytes(2, "big"),
                         sport=56002,
                         dport=56002)


class MainWindow(QMainWindow, Ui_MainWindow):
    send_multicast_usage_mode_signal = Signal(int)
    send_ml_fuse_id_on_signal = Signal(int)
    send_ml_fuse_id_off_signal = Signal(int)
    send_mr_fuse_id_on_signal = Signal(int)
    send_mr_fuse_id_off_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        if not self.check_scapy_driver():
            self.show_driver_error()

        self.interfaces_list = []
        self.comboBox_UsageMode.addItems(['convenient',
                                          'RobotDriving',
                                          'SystemUpdate',
                                          'Driving',
                                          'Abandoned'])

        self.someip_send_thread = QThread()
        self.someip_sender = ZCUSomeipSender(parent=self)
        self.someip_sender.moveToThread(self.someip_send_thread)
        self.someip_send_thread.start()
        self.multicast_usage_mode_timer = QTimer()
        self.multicast_usage_mode_timer.timeout.connect(self.send_multicast_usage_mode)

        self.pushButton_SendUsageMode.setIcon(IconEngine.get_icon('start', 'orange'))

        self.update_interfaces()
        self.someip_sender.iface = self.interfaces_list[0]

        self.comboBox_ifaces.currentIndexChanged.connect(self.update_interface)
        self.pushButton_IfacesRefresh.clicked.connect(self.update_interfaces)
        # self.pushButton_SendUsageMode.clicked.connect(self.send_multicast_usage_mode)
        self.pushButton_SendUsageMode.clicked.connect(self.toggle_send_multicast_usage_mode_timer)
        self.pushButton_MLFuseIDOn.clicked.connect(self.send_ml_fuse_id_on)
        self.pushButton_MLFuseIDOff.clicked.connect(self.send_ml_fuse_id_off)
        self.pushButton_MRFuseIDOn.clicked.connect(self.send_mr_fuse_id_on)
        self.pushButton_MRFuseIDOff.clicked.connect(self.send_mr_fuse_id_off)

        self.send_ml_fuse_id_on_signal.connect(self.someip_sender.send_ml_fuse_id_on)
        self.send_ml_fuse_id_off_signal.connect(self.someip_sender.send_ml_fuse_id_off)
        self.send_mr_fuse_id_on_signal.connect(self.someip_sender.send_mr_fuse_id_on)
        self.send_mr_fuse_id_off_signal.connect(self.someip_sender.send_mr_fuse_id_off)
        self.send_multicast_usage_mode_signal.connect(self.someip_sender.send_multicast_usage_mode)
        self.json_path = 'fuse_id.json'
        self.fuse_id_config = {}
        self.init_ml_fuseid_tableview()
        self.init_mr_fuseid_tableview()
        self.load_data()

    def load_data(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.fuse_id_config = json.load(f)
                    for item in self.fuse_id_config['ml_fuse_id']:
                        self.ml_fuseid_model.appendRow([
                            QStandardItem(str(item.get("FuseID", ""))),
                            QStandardItem(str(item.get("comment", "")))
                        ])
                    for item in self.fuse_id_config['mr_fuse_id']:
                        self.mr_fuseid_model.appendRow([
                            QStandardItem(str(item.get("FuseID", ""))),
                            QStandardItem(str(item.get("comment", "")))
                        ])
            except:
                pass

    def save_to_json(self):
        self.fuse_id_config['ml_fuse_id'].clear()
        self.fuse_id_config['mr_fuse_id'].clear()
        for row in range(self.ml_fuseid_model.rowCount()):
            self.fuse_id_config['ml_fuse_id'].append({
                "FuseID": self.ml_fuseid_model.item(row, 0).text() if self.ml_fuseid_model.item(row, 0) else "",
                "comment": self.ml_fuseid_model.item(row, 1).text() if self.ml_fuseid_model.item(row, 1) else ""
            })
        for row in range(self.mr_fuseid_model.rowCount()):
            self.fuse_id_config['mr_fuse_id'].append({
                "FuseID": self.mr_fuseid_model.item(row, 0).text() if self.mr_fuseid_model.item(row, 0) else "",
                "comment": self.mr_fuseid_model.item(row, 1).text() if self.mr_fuseid_model.item(row, 1) else ""
            })
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.fuse_id_config, f, indent=4, ensure_ascii=False)

    def init_ml_fuseid_tableview(self):
        self.ml_fuseid_model = QStandardItemModel()
        self.ml_fuseid_model.setHorizontalHeaderLabels(["FuseID", "Comment"])
        self.tableView_FuseIDL.setModel(self.ml_fuseid_model)
        self.tableView_FuseIDL.horizontalHeader().setStretchLastSection(True)
        # 设置为不可直接双击编辑（如果需要点击即选中的话，建议设为只读或整行选中）
        self.tableView_FuseIDL.setEditTriggers(QTableView.DoubleClicked)
        self.tableView_FuseIDL.setSelectionBehavior(QTableView.SelectRows)
        self.tableView_FuseIDL.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView_FuseIDL.customContextMenuRequested.connect(self.show_context_menu_ml)
        self.tableView_FuseIDL.clicked.connect(self.on_ml_table_clicked)

    def init_mr_fuseid_tableview(self):
        self.mr_fuseid_model = QStandardItemModel()
        self.mr_fuseid_model.setHorizontalHeaderLabels(["FuseID", "Comment"])
        self.tableView_FuseIDR.setModel(self.mr_fuseid_model)
        self.tableView_FuseIDR.horizontalHeader().setStretchLastSection(True)
        # 设置为不可直接双击编辑（如果需要点击即选中的话，建议设为只读或整行选中）
        self.tableView_FuseIDR.setEditTriggers(QTableView.DoubleClicked)
        self.tableView_FuseIDR.setSelectionBehavior(QTableView.SelectRows)
        self.tableView_FuseIDR.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView_FuseIDR.customContextMenuRequested.connect(self.show_context_menu_mr)
        self.tableView_FuseIDR.clicked.connect(self.on_mr_table_clicked)

    def on_ml_table_clicked(self, index):
        """左键点击行：获取第一列值"""
        item = self.ml_fuseid_model.item(index.row(), 0)
        if item:
            fuse_id = item.text()
            self.lineEdit_MLFuseid.setText(fuse_id)

    def on_mr_table_clicked(self, index):
        """左键点击行：获取第一列值"""
        item = self.mr_fuseid_model.item(index.row(), 0)
        if item:
            fuse_id = item.text()
            self.lineEdit_MRFuseID.setText(fuse_id)



    def show_context_menu_mr(self, pos):
        """右键点击：弹出菜单"""
        menu = QMenu(self)

        # 创建菜单项
        add_action = QAction("新增行", self)
        del_action = QAction("删除选中行", self)

        # 连接动作
        add_action.triggered.connect(self.add_row_mr)
        del_action.triggered.connect(self.delete_row_mr)

        menu.addAction(add_action)
        menu.addAction(del_action)

        # 在鼠标当前位置显示菜单
        menu.exec(QCursor.pos())

    def add_row_mr(self):
        # 默认添加一行空数据，你可以之后双击修改
        self.mr_fuseid_model.appendRow([QStandardItem(""), QStandardItem("备注")])

    def delete_row_mr(self):
        # 获取选中的行索引
        selection_model = self.tableView_FuseIDR.selectionModel()
        indexes = selection_model.selectedRows()

        if not indexes:
            return

        # 倒序删除，防止索引错乱
        for index in sorted(indexes, reverse=True):
            self.mr_fuseid_model.removeRow(index.row())

    def show_context_menu_ml(self, pos):
        """右键点击：弹出菜单"""
        menu = QMenu(self)

        # 创建菜单项
        add_action = QAction("新增行", self)
        del_action = QAction("删除选中行", self)

        # 连接动作
        add_action.triggered.connect(self.add_row_ml)
        del_action.triggered.connect(self.delete_row_ml)

        menu.addAction(add_action)
        menu.addAction(del_action)

        # 在鼠标当前位置显示菜单
        menu.exec(QCursor.pos())

    def add_row_ml(self):
        # 默认添加一行空数据，你可以之后双击修改
        self.ml_fuseid_model.appendRow([QStandardItem(""), QStandardItem("备注")])

    def delete_row_ml(self):
        # 获取选中的行索引
        selection_model = self.tableView_FuseIDL.selectionModel()
        indexes = selection_model.selectedRows()

        if not indexes:
            return

        # 倒序删除，防止索引错乱
        for index in sorted(indexes, reverse=True):
            self.ml_fuseid_model.removeRow(index.row())

    def show_driver_error(self):
        """弹出带有超链接的驱动缺失警告窗"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("驱动缺失")

        # 使用 HTML 格式定义文本和链接
        content = (
            "未检测到必要的抓包驱动 (Npcap)！<br><br>"
            "请前往官网下载并安装：<br>"
            "<a href='https://npcap.com/#download'>https://npcap.com/#download</a><br><br>"
        )

        msg.setText(content)
        # 关键步骤：允许用户点击链接并确保它是富文本格式
        msg.setTextFormat(Qt.RichText)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg.setStandardButtons(QMessageBox.Ok)
        # 如果你想驱动不安装就直接关闭程序，可以解开下面这行的注释
        msg.finished.connect(lambda: sys.exit())
        msg.exec()

    @staticmethod
    def check_scapy_driver():
        # 在 Windows 上，Scapy 主要依赖 Npcap 或 WinPcap
        # conf.use_pcap 为 True 表示底层 pcap 库可用
        if conf.use_pcap:
            # print("✅ 检测到底层抓包驱动 (Npcap/WinPcap/libpcap) 已安装。")
            return True
        else:
            # print("❌ 未检测到合适的抓包驱动。")
            return False

    def toggle_send_multicast_usage_mode_timer(self):
        if self.multicast_usage_mode_timer.isActive():
            self.multicast_usage_mode_timer.stop()
            self.pushButton_SendUsageMode.setIcon(IconEngine.get_icon('start', 'orange'))
        else:
            self.multicast_usage_mode_timer.start(1000)
            self.pushButton_SendUsageMode.setIcon(IconEngine.get_icon('stop', 'red'))



    def send_ml_fuse_id_on(self):
        fuse_id_str = self.lineEdit_MLFuseid.text()
        try:
            fuse_id = int(fuse_id_str, 16)
            self.send_ml_fuse_id_on_signal.emit(fuse_id)
        except Exception as e:
            pass

    def send_ml_fuse_id_off(self):
        fuse_id_str = self.lineEdit_MLFuseid.text()
        try:
            fuse_id = int(fuse_id_str, 16)
            self.send_ml_fuse_id_off_signal.emit(fuse_id)
        except Exception as e:
            pass

    def send_mr_fuse_id_on(self):
        fuse_id_str = self.lineEdit_MRFuseID.text()
        try:
            fuse_id = int(fuse_id_str, 16)
            self.send_mr_fuse_id_on_signal.emit(fuse_id)
        except Exception as e:
            pass

    def send_mr_fuse_id_off(self):
        fuse_id_str = self.lineEdit_MRFuseID.text()
        try:
            fuse_id = int(fuse_id_str, 16)
            self.send_mr_fuse_id_off_signal.emit(fuse_id)
        except Exception as e:
            pass

    def send_multicast_usage_mode(self):
        usagemode = self.comboBox_UsageMode.currentIndex()
        self.send_multicast_usage_mode_signal.emit(usagemode)

    @Slot(int)
    def update_interface(self, index):
        self.someip_sender.iface = self.interfaces_list[index]

    def update_interfaces(self):

        interfaces = conf.ifaces
        self.interfaces_list.clear()
        for name, iface_obj in interfaces.items():
            if iface_obj.mac != '':
                self.interfaces_list.append(iface_obj.description)
        self.comboBox_ifaces.blockSignals(True)
        self.comboBox_ifaces.clear()
        self.comboBox_ifaces.addItems(self.interfaces_list)
        self.comboBox_ifaces.blockSignals(False)

    def closeEvent(self, event) -> None:
        self.save_to_json()
        event.accept()
        self.multicast_usage_mode_timer.stop()
        if self.someip_send_thread:
            self.someip_send_thread.quit()
            if self.someip_send_thread.wait(3000):  # 等待3秒超时
                pass
            else:
                pass
