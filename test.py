import scapy
from scapy.config import conf
from scapy.contrib.automotive.someip import SOMEIP, SDEntry_Service, SDOption_IP4_EndPoint, SD
from scapy.fields import XByteEnumField
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether  # 关键：导入以太网二层头
from scapy.main import load_contrib
from scapy.packet import Raw, bind_top_down, ls
from scapy.sendrecv import sendp  # 关键：改用二层发送函数sendp

load_contrib('automotive.someip')
# interfaces = conf.ifaces
# print(interfaces)
"""
Source   Index  Name                                       MAC                 IPv4            IPv6                     
libpcap  1      Software Loopback Interface 1              00:00:00:00:00:00   127.0.0.1       ::1                      
libpcap  12     WAN Miniport (IP)                                                                                       
libpcap  15     Microsoft Wi-Fi Direct Virtual Adapter #2  22:c1:9b:af:b5:2c   169.254.85.147  fe80::3ab8:e01d:f73d:4b70
libpcap  17     WAN Miniport (Network Monitor)                                                                          
libpcap  18     Intel(R) Ethernet Connection (13) I219-LM  88:88:88:88:87:88   169.254.172.29  fe80::5980:da38:e77d:5ea9
libpcap  22     Bluetooth Device (Personal Area Network)   Intel:af:b5:30      169.254.212.30  fe80::48ae:3b4:578d:3210 
libpcap  26     Hyper-V Virtual Ethernet Adapter           Microsoft:2e:4e:00  172.26.96.1     fe80::1741:57bc:cf6d:171e
libpcap  4      Intel(R) Wi-Fi 6 AX201 160MHz              Intel:af:b5:2c      10.168.47.232   fe80::2ab7:10e4:e896:5fde
libpcap  5      WAN Miniport (IPv6)                                                                                     
libpcap  7      Microsoft Wi-Fi Direct Virtual Adapter     Intel:af:b5:2d      169.254.116.11  fe80::95ce:ec8:8a2a:857c 
"""

# ===================== 核心配置：手动指定 MAC + 网卡 =====================
IFACE = "Hyper-V Virtual Ethernet Adapter"          # 发送网卡（必改！如回环lo/物理网卡eth0/车载vcan0/ens33）
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
ea.index_1 = 0
ea.n_opt_1 = 1
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
p = ether / i / u / SOMEIP() / sd


sendp(p, iface=IFACE, verbose=0)  # verbose=0 关闭发送日志，可选
print(f"已通过网卡[{IFACE}]发送SOMEIP报文 | 源MAC[{SRC_MAC}] → 目标MAC[{DST_MAC}]")
