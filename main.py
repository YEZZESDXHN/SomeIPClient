import time
import struct
import socket
import logging
from threading import Thread
from functools import partial

# Scapy & Protocol
from scapy.all import *
from scapy.contrib.automotive.someip import SOMEIP, SDEntry_Service, SDOption_IP4_EndPoint, SD
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

# State Machine
from transitions import Machine

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# ================= 配置区域 =================
IFACE_NAME = "Hyper-V Virtual Ethernet Adapter"  # 请修改为你的真实网卡
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)


# 工具函数
def get_multicast_mac(ip):
    if not ip.startswith("224."): return "ff:ff:ff:ff:ff:ff"
    ip_bytes = struct.unpack("!I", socket.inet_aton(ip))[0]
    mac_num = 0x01005E000000 | (ip_bytes & 0x7FFFFF)
    return ":".join([f"{(mac_num >> i) & 0xFF:02x}" for i in (40, 32, 24, 16, 8, 0)])


# 基类
class SomeIPBase:
    def __init__(self, iface, src_mac, src_ip, srv_id, sd_mcast_ip="224.224.224.245"):
        self.iface = iface
        self.src_mac = src_mac
        self.src_ip = src_ip
        self.srv_id = srv_id

        self.sd_mcast_ip = sd_mcast_ip
        self.sd_mcast_mac = get_multicast_mac(self.sd_mcast_ip)
        self.sd_port = 30490
        self.app_port = 30509  # 应用数据端口

        self.running = False
        self.sniffer = None

    def start_network(self):
        self.running = True
        # 【修改点】同时监听 SD 端口和 APP 端口
        bpf_filter = f"udp port {self.sd_port} or udp port {self.app_port}"

        self.sniffer = AsyncSniffer(
            iface=self.iface,
            prn=self._packet_callback,
            filter=bpf_filter,
            store=False
        )
        self.sniffer.start()
        print(f"[{self.__class__.__name__}] 网络层启动 (监听 {self.sd_port} & {self.app_port})")

    def stop_network(self):
        self.running = False
        if self.sniffer: self.sniffer.stop()

    def _packet_callback(self, pkt):
        if not self.running:
            return
        if Ether in pkt and pkt[Ether].src.lower() == self.src_mac.lower():
            return

        # 1. SD 报文处理
        if SOMEIP in pkt and SD in pkt:
            self.on_sd_message(pkt[SOMEIP], pkt[SD])

        # 2. 【新增】普通方法调用处理 (Service ID 匹配且没有 SD 层)
        elif SOMEIP in pkt and not (SD in pkt):
            sip = pkt[SOMEIP]
            if sip.srv_id == self.srv_id:
                # 提取 Payload
                payload = pkt[Raw].load if Raw in pkt else b''
                self.on_someip_request(pkt, sip, payload)

    # --- 虚函数，由子类实现 ---
    def on_sd_message(self, someip, sd):
        pass

    def on_someip_request(self, pkt, someip, payload):
        pass

    # 发送响应 (用于 RR, Getter, Setter)
    def send_response(self, req_pkt, response_payload):
        req_sip = req_pkt[SOMEIP]

        # 交换 IP/Port
        eth = Ether(src=self.src_mac, dst=req_pkt[Ether].src)
        ip = IP(src=self.src_ip, dst=req_pkt[IP].src)
        udp = UDP(sport=self.app_port, dport=req_pkt[UDP].sport)

        sip = SOMEIP()
        sip.srv_id = req_sip.srv_id
        sip.method_id = req_sip.method_id
        sip.client_id = req_sip.client_id
        sip.session_id = req_sip.session_id
        sip.proto_ver = req_sip.proto_ver
        sip.iface_ver = req_sip.iface_ver
        sip.msg_type = 0x80  # RESPONSE
        sip.retcode = 0x00  # E_OK

        # 只有 payload 不为空才加 Raw
        if response_payload:
            pkt = eth / ip / udp / sip / Raw(load=response_payload)
        else:
            pkt = eth / ip / udp / sip

        sendp(pkt, iface=self.iface, verbose=0)

    # --- 发送请求 (用于客户端测试) ---
    def send_request(self, method_id, payload, dst_ip, msg_type=0x00):
        dst_mac = get_multicast_mac(dst_ip) if dst_ip.startswith("224.") else "ff:ff:ff:ff:ff:ff"  # 简化处理

        eth = Ether(src=self.src_mac, dst=dst_mac)
        ip = IP(src=self.src_ip, dst=dst_ip)
        udp = UDP(sport=55000, dport=self.app_port)  # 随机源端口

        sip = SOMEIP()
        sip.srv_id = self.srv_id
        sip.method_id = method_id
        sip.msg_type = msg_type  # 0x00=Request, 0x01=Request_No_Return
        sip.client_id = 0x1111
        sip.session_id = int(time.time()) & 0xFFFF

        if payload:
            pkt = eth / ip / udp / sip / Raw(load=payload)
        else:
            pkt = eth / ip / udp / sip

        sendp(pkt, iface=self.iface, verbose=0)

    # --- SD 发送 (保持不变) ---
    def send_sd(self, entry_type, options=None):
        eth = Ether(src=self.src_mac, dst=self.sd_mcast_mac)
        ip = IP(src=self.src_ip, dst=self.sd_mcast_ip)
        udp = UDP(sport=self.sd_port, dport=self.sd_port)
        ea = SDEntry_Service(type=entry_type, srv_id=self.srv_id, inst_id=0x5678, ttl=3)
        sd = SD()
        if options:
            ea.index_1 = 0
            ea.n_opt_1 = 1
            sd.set_optionArray(options)
        sd.set_entryArray(ea)
        sendp(eth / ip / udp / SOMEIP() / sd, iface=self.iface, verbose=0)

    # --- Event 发送 (保持不变) ---
    def send_event(self, method_id, payload_data, dst_ip, dst_port):
        dst_mac = get_multicast_mac(dst_ip) if dst_ip.startswith("224.") else "ff:ff:ff:ff:ff:ff"
        eth = Ether(src=self.src_mac, dst=dst_mac)
        ip = IP(src=self.src_ip, dst=dst_ip)
        udp = UDP(sport=self.app_port, dport=dst_port)
        sip = SOMEIP(msg_id=method_id, msg_type=0x02, srv_id=self.srv_id)  # Notification
        pkt = eth / ip / udp / sip / Raw(load=payload_data)
        sendp(pkt, iface=self.iface, verbose=0)


# Provider (实现 RR, FF, Getter, Setter)
class SomeIPProvider(SomeIPBase):
    states = ['unsubscribed', 'subscribed']

    def __init__(self, iface, src_mac, src_ip):
        super().__init__(iface, src_mac, src_ip)

        # 1. 内部数据存储 (供 Getter/Setter 使用)
        self.internal_value = 100  # 初始值

        # 2. 方法路由表 (Hardcoded for logic demo)
        # 格式: ID -> (类型, 处理函数)
        self.methods = {
            0x0001: ('RR', self._handle_rr_add),  # Request-Response: 加法
            0x0002: ('FF', self._handle_ff_log),  # Fire & Forget: 日志
            0x0003: ('SET', self._handle_setter),  # Setter: 设置值
            0x0004: ('GET', self._handle_getter)  # Getter: 获取值
        }

        # 3. 状态机与调度器
        self.machine = Machine(model=self, states=SomeIPProvider.states, initial='unsubscribed')
        self.machine.add_transition('got_subscriber', 'unsubscribed', 'subscribed')
        self.scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(20)})
        self.subscriber_ip = "224.224.224.245"

    def start(self):
        self.start_network()
        self.scheduler.add_job(self._job_send_offer, 'interval', seconds=2.0)
        self.scheduler.add_job(self._job_send_speed, 'interval', seconds=1.0)  # 1Hz Event
        self.scheduler.start()
        print("[Provider] 服务启动。支持方法: 0x0001(Add), 0x0002(Log), 0x0003(Set), 0x0004(Get)")

    def stop(self):
        self.stop_network()
        self.scheduler.shutdown()

    # --- 调度器 Job ---
    def _job_send_offer(self):
        oa = SDOption_IP4_EndPoint(addr=self.src_ip, port=30509, l4_proto=0x11)
        self.send_sd(entry_type=0x01, options=oa)

    def _job_send_speed(self):
        if self.state == 'subscribed':
            data = struct.pack("!I", int(time.time() % 100))
            self.send_event(0x8001, data, self.subscriber_ip, 30509)

    # --- 【核心】处理请求的回调 ---
    def on_someip_request(self, pkt, someip, payload):
        mid = someip.method_id

        if mid not in self.methods:
            print(f"[Prov] 未知方法调用: {hex(mid)}")
            # 这里应该回 E_UNKNOWN_METHOD，省略
            return

        method_type, handler = self.methods[mid]

        # print(f"[Prov] 收到 {method_type} 请求 (ID={hex(mid)})")

        # 执行业务逻辑
        response_data = handler(payload)

        # 根据类型决定是否回包
        if method_type == 'FF':
            return  # Fire & Forget 不回包

        # RR, GET, SET 都要回包
        self.send_response(pkt, response_data)

    # --- 具体业务逻辑实现 ---
    def _handle_rr_add(self, payload):
        """RR: 接收两个 int, 返回和"""
        try:
            a, b = struct.unpack("!II", payload)
            res = a + b
            print(f"  -> 执行 Add: {a} + {b} = {res}")
            return struct.pack("!I", res)
        except:
            return b'\x00'

    def _handle_ff_log(self, payload):
        """FF: 打印日志，无返回"""
        try:
            msg = payload.decode('utf-8')
            print(f"  -> [Log Service] 收到客户端日志: {msg}")
        except:
            pass
        return None

    def _handle_setter(self, payload):
        """Setter: 修改内部变量，返回新值"""
        try:
            new_val = struct.unpack("!I", payload)[0]
            print(f"  -> Setter: 修改 internal_value {self.internal_value} -> {new_val}")
            self.internal_value = new_val
            return payload  # 通常 Setter 返回设置后的值
        except:
            return b'\x00'

    def _handle_getter(self, payload):
        """Getter: 读取内部变量"""
        print(f"  -> Getter: 读取 internal_value = {self.internal_value}")
        return struct.pack("!I", self.internal_value)

    # --- SD 处理 ---
    def on_sd_message(self, someip, sd):
        for entry in sd.entry_array:
            if entry.type == 0x00 and entry.srv_id == self.srv_id:
                if self.state == 'unsubscribed':
                    print(f"\n[Prov] 收到 FindService -> Subscribed!\n")
                    self.got_subscriber()


# Subscriber (及测试 Client)
class SomeIPSubscriber(SomeIPBase):
    states = ['unsubscribed', 'subscribed']

    def __init__(self, iface, src_mac, src_ip):
        super().__init__(iface, src_mac, src_ip)
        self.machine = Machine(model=self, states=SomeIPSubscriber.states, initial='unsubscribed')
        self.machine.add_transition('receive_offer', 'unsubscribed', 'subscribed')
        self.scheduler = BackgroundScheduler()
        self.provider_ip = "192.168.10.1"  # 假设知道 Provider IP

    def start(self):
        self.start_network()
        self.scheduler.add_job(self._job_find, 'interval', seconds=2.0)
        self.scheduler.start()

    def stop(self):
        self.stop_network()
        self.scheduler.shutdown()

    def _job_find(self):
        if self.state == 'unsubscribed':
            self.send_sd(entry_type=0x00)

    def on_sd_message(self, someip, sd):
        for entry in sd.entry_array:
            if entry.type == 0x01 and entry.srv_id == self.srv_id:
                if self.state == 'unsubscribed':
                    print("\n[Sub] 收到 Offer -> Ready\n")
                    self.receive_offer()
                    # 订阅成功后，启动测试线程来调用方法
                    Thread(target=self.run_method_tests).start()

    def on_someip_request(self, pkt, someip, payload):
        # 处理收到的 Response (0x80)
        if someip.msg_type == 0x80:
            mid = someip.method_id
            if mid == 0x0001:  # Add Result
                res = struct.unpack("!I", payload)[0]
                print(f"[Client] 收到 RR Add 结果: {res}")
            elif mid == 0x0003:  # Set Result
                res = struct.unpack("!I", payload)[0]
                print(f"[Client] 收到 Setter 确认: {res}")
            elif mid == 0x0004:  # Get Result
                res = struct.unpack("!I", payload)[0]
                print(f"[Client] 收到 Getter 结果: {res}")

    def run_method_tests(self):
        """模拟业务调用序列"""
        time.sleep(1)
        print("\n--- [Test] 1. 调用 RR Add(10, 20) ---")
        self.send_request(0x0001, struct.pack("!II", 10, 20), self.provider_ip)

        time.sleep(1)
        print("\n--- [Test] 2. 调用 FF Log('Hello') ---")
        # FF 的 msg_type 必须是 0x01 (Request_No_Return)
        self.send_request(0x0002, b"Hello From Client", self.provider_ip, msg_type=0x01)

        time.sleep(1)
        print("\n--- [Test] 3. 调用 Getter (当前值) ---")
        self.send_request(0x0004, b'', self.provider_ip)

        time.sleep(1)
        print("\n--- [Test] 4. 调用 Setter (设置为 888) ---")
        self.send_request(0x0003, struct.pack("!I", 888), self.provider_ip)

        time.sleep(1)
        print("\n--- [Test] 5. 再次调用 Getter (确认修改) ---")
        self.send_request(0x0004, b'', self.provider_ip)


# ================= 4. 主程序 =================
if __name__ == "__main__":
    MAC_PROV = "02:00:00:00:00:01"
    MAC_SUB = "02:00:00:00:00:02"

    prov = SomeIPProvider(IFACE_NAME, MAC_PROV, "192.168.10.1")
    sub = SomeIPSubscriber(IFACE_NAME, MAC_SUB, "192.168.10.2")

    try:
        prov.start()
        time.sleep(1)
        sub.start()  # Sub 启动后会发 Find -> 收到 Offer -> 触发 run_method_tests

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        prov.stop()
        sub.stop()