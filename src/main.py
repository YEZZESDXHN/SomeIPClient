from scapy.interfaces import show_interfaces

from src.SomeIPLab import MyLab

def main():    
    test = MyLab()
    a = test.start_someip_server(ecu_pair=("PCU_Proxy_Frontend", "IVC"), service_id=16384)
    print(f"[RESULTADO] : {a[0]} | Comentario: {a[1]}")

if __name__ == "__main__":
    # show_interfaces()
    main()
