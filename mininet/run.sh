BMV2_SWITCH_EXE="simple_switch_grpc"

p4c --target bmv2 --arch v1model --p4runtime-files demo0216.p4info.txt --std p4-16 -o build p4src/basic.p4
sudo ./demo0216.py --behavioral-exe simple_switch_grpc --json build/basic.json
