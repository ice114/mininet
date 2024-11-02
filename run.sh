BMV2_SWITCH_EXE="simple_switch_grpc"
p4c --target bmv2 --arch v1model --p4runtime-files GAIA1107.p4info.txt  --std p4-16 -o build p4src/GAIA1107.p4
sudo python3 ./main1111.py --behavioral-exe simple_switch_grpc --json doc/GAIA1107.json --quiet   --log-dir logs
