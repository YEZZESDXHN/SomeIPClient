import scapy
from scapy.contrib.automotive.someip import SOMEIP, SDEntry_Service, SDOption_IP4_EndPoint, SD
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether  # 关键：导入以太网二层头
from scapy.main import load_contrib
from scapy.packet import Raw, bind_top_down
from scapy.sendrecv import sendp  # 关键：改用二层发送函数sendp

load_contrib('automotive.someip')

# ===================== 核心配置：手动指定 MAC + 网卡 =====================
IFACE = ""          # 发送网卡（必改！如回环lo/物理网卡eth0/车载vcan0/ens33）
SRC_MAC = "00:00:00:00:00:00"  # 源MAC（自身网卡MAC，回环可用全0）
DST_MAC = "00:00:00:00:00:00"  # 目标MAC（对方设备MAC，回环可用全0）
# ==========================================================================

# # 1. 原有代码：构造IP/UDP/SOMEIP层（完全不变）
u = UDP(sport=30509, dport=30509)
i = IP(src="127.0.0.1", dst="127.0.0.1")  # IP可保留，二层发送不影响上层
sip = SOMEIP()
sip.iface_ver = 0
sip.proto_ver = 1
sip.msg_type = "REQUEST"
sip.retcode = "E_OK"
sip.srv_id = 0x1234
sip.method_id = 0x421
sip.add_payload(Raw("Hello"))

print(sip.build().hex(' '))

# 2. 关键：封装Ether二层头（指定源/目标MAC）
ether = Ether(src=SRC_MAC, dst=DST_MAC)

# 3. 二层报文完整封装：Ether + IP + UDP + SOMEIP
p = ether / i / u / sip

# 4. 关键：用sendp发送，显式指定网卡iface，无ARP请求
sendp(p, iface=IFACE, verbose=0)  # verbose=0 关闭发送日志，可选
print(f"已通过网卡[{IFACE}]发送SOMEIP报文 | 源MAC[{SRC_MAC}] → 目标MAC[{DST_MAC}]")


u = UDP(sport=30490, dport=30490)
i = IP(src="192.168.0.13", dst="224.224.224.245")

ea = SDEntry_Service()

ea.type = 0x01
ea.srv_id = 0x1234
ea.inst_id = 0x5678
ea.major_ver = 0x00
ea.ttl = 3

oa = SDOption_IP4_EndPoint()
oa.addr = "192.168.0.13"
oa.l4_proto = 0x11
oa.port = 30509

sd = SD()
sd.set_entryArray(ea)
sd.set_optionArray(oa)


print(sd.build().hex(' '))


ether = Ether(src=SRC_MAC, dst=DST_MAC)
p = ether / i / u / sd


sendp(p, iface=IFACE, verbose=0)  # verbose=0 关闭发送日志，可选
print(f"已通过网卡[{IFACE}]发送SOMEIP报文 | 源MAC[{SRC_MAC}] → 目标MAC[{DST_MAC}]")
