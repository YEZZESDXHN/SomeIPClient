# from scapy.interfaces import show_interfaces
from scapy.config import conf

from src.SomeIPLab import MyLab

def main():
    # -----------------viu_ml mr-------------------
    viu_list = ["VIU_ML", 'VIU_MR']
    selected_viu = None
    # 按序号列出车辆模式
    print("请选择ECU：")
    for i, mode in enumerate(viu_list):
        # 序号从 1 开始
        print(f"[{i}] {mode}")

    while selected_viu is None:
        try:
            selection = input("请输入模式序号: ")
            choice_index = int(selection)

            if 0 <= choice_index <= len(viu_list) - 1:
                selected_viu = viu_list[choice_index]
                # print(f"✅ 已选择模式: **{selected_mode}**")

            else:
                # 序号不在范围内
                print(f"输入错误: 序号 {choice_index} 不在有效范围 [1 - {len(viu_list)}] 内，请重新输入。")

        except ValueError:
            # 输入不是一个有效的整数
            print("输入错误: 请输入一个有效的数字序号。")


    # -----------------网络接口-------------------
    interfaces = conf.ifaces
    interfaces_list = []
    for name, iface_obj in interfaces.items():
        if iface_obj.mac != '':
            interfaces_list.append(iface_obj.description)
    # print(interfaces_list)

    print("\n请选择一个接口，输入对应的序号：")
    for i, description in enumerate(interfaces_list):
        # 序号从 1 开始
        print(f"[{i + 1}] {description}")

    # 2.2 循环接收用户输入，直到输入合法
    while True:
        try:
            # 获取用户输入
            selection = input("请输入序号: ")

            # 将输入转换为整数
            choice_index = int(selection)

            # 检查序号是否在有效范围内 (1 到 列表长度)
            if 1 <= choice_index <= len(interfaces_list):
                # 获取用户选择的接口描述
                selected_interface = interfaces_list[choice_index - 1]
                # print(f"\n您选择了序号 **{choice_index}**: **{selected_interface}**")

                # 退出循环
                break
            else:
                # 序号不在范围内
                print(f"输入错误: 序号 {choice_index} 不在有效范围 [1 - {len(interfaces_list)}] 内，请重新输入。")

        except ValueError:
            # 输入不是一个有效的整数
            print("输入错误: 请输入一个有效的数字序号。")

        except Exception as e:
            # 处理其他可能的错误
            print(f"发生未知错误: {e}")

    # -----------------车辆模式-------------------
    UsageModes_enum = ["convenient", 'RobotDriving', 'SystemUpdate', 'Driving', 'Abandoned']
    # selected_mode = None
    # 按序号列出车辆模式
    # print("请选择一个车辆模式，输入对应的序号：")
    # for i, mode in enumerate(UsageModes_enum):
    #     # 序号从 1 开始
    #     print(f"[{i}] {mode}")
    #
    # while True:
    #     try:
    #         selection = input("请输入模式序号: ")
    #         choice_index = int(selection)
    #
    #         if 0 <= choice_index <= len(UsageModes_enum)-1:
    #             selected_mode_index = choice_index
    #             # print(f"✅ 已选择模式: **{selected_mode}**")
    #
    #             # 退出循环
    #             break
    #         else:
    #             # 序号不在范围内
    #             print(f"输入错误: 序号 {choice_index} 不在有效范围 [1 - {len(UsageModes_enum)}] 内，请重新输入。")
    #
    #     except ValueError:
    #         # 输入不是一个有效的整数
    #         print("输入错误: 请输入一个有效的数字序号。")



    test = MyLab()
    # test.interface = 'Ethernet 5'
    test.interface = selected_interface
    test.event_payload_length = 1
    # test.event_payload = b'\x01'

    while True:
        print("请选择一个车辆模式，输入对应的序号：")
        for i, mode in enumerate(UsageModes_enum):
            # 序号从 1 开始
            print(f"[{i}] {mode}")

        while True:
            try:
                selection = input("请输入模式序号: ")
                choice_index = int(selection)

                if 0 <= choice_index <= len(UsageModes_enum) - 1:
                    selected_mode_index = choice_index
                    # print(f"✅ 已选择模式: **{selected_mode}**")

                    # 退出循环
                    break
                else:
                    # 序号不在范围内
                    print(f"输入错误: 序号 {choice_index} 不在有效范围 [1 - {len(UsageModes_enum)}] 内，请重新输入。")

            except ValueError:
                # 输入不是一个有效的整数
                print("输入错误: 请输入一个有效的数字序号。")
        test.event_payload = selected_mode_index.to_bytes(test.event_payload_length, 'little')
        if selected_viu == 'VIU_ML':
            a = test.start_someip_server(ecu_pair=("S32G", "VIU_ML"), service_id=16384)
        elif selected_viu == 'VIU_MR':
            a = test.start_someip_server(ecu_pair=("S32G", "VIU_MR"), service_id=16384)

        print(f"[RESULTADO] : {a[0]} | Comentario: {a[1]}")

if __name__ == "__main__":
    main()
