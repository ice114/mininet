#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

ports=[[1,1],[3,0]]
def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s11 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s11',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s11-p4runtime-requests.txt')
        s12 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s12',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s12-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s11.MasterArbitrationUpdate()
        s12.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s11.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s12.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s2")
        port=[1,1]
        # Write the rules that tunnel traffic from h1 to h2
        writeTunnelRules(p4info_helper, ingress_sw=s11, egress_sw=s12, ports=port,
                         dst_eth_addr="08:00:00:00:01:02", dst_ip_addr="10.0.1.2")
        port1=[3,0]
        writeTunnelRules2(p4info_helper, ingress_sw=s11, egress_sw=s12, ports=port1,
                         dst_eth_addr="08:00:00:00:01:02", dst_ip_addr="10.0.1.2")
        # Write the rules that tunnel traffic from h2 to h1
        writeTunnelRules3(p4info_helper, ingress_sw=s11, egress_sw=s12,
                         dst_eth_addr="08:00:00:00:01:02", dst_ip_addr="10.0.1.2")

        writeTunnelRules(p4info_helper, ingress_sw=s12, egress_sw=s11, ports=port,
                         dst_eth_addr="08:00:00:00:01:01", dst_ip_addr="10.0.1.1")

        writeTunnelRules2(p4info_helper, ingress_sw=s12, egress_sw=s11, ports=port1,
                          dst_eth_addr="08:00:00:00:01:01", dst_ip_addr="10.0.1.1")
        # Write the rules that tunnel traffic from h2 to h1
        writeTunnelRules3(p4info_helper, ingress_sw=s12, egress_sw=s11,
                          dst_eth_addr="08:00:00:00:01:01", dst_ip_addr="10.0.1.1")
        # TODO Uncomment the following two lines to read table entries from s1 and s2
        readTableRules(p4info_helper, s11)
        readTableRules(p4info_helper, s12)

        # Print the tunnel counters every 2 seconds
        while True:
            sleep(2)
            print '\n----- Reading tunnel counters -----'
            printCounter(p4info_helper, s11, "MyIngress.ingressTunnelCounter", 100)
            printCounter(p4info_helper, s12, "MyIngress.egressTunnelCounter", 100)
            printCounter(p4info_helper, s12, "MyIngress.ingressTunnelCounter", 200)
            printCounter(p4info_helper, s11, "MyIngress.egressTunnelCounter", 200)

    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

def writeTunnelRules(p4info_helper, ingress_sw, egress_sw, ports,
                     dst_eth_addr, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm_add",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.addlabel",
        action_params={
            "port": ports[0],
            "flag": ports[1],
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name

def writeTunnelRules2(p4info_helper, ingress_sw, egress_sw, ports,
                     dst_eth_addr, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm_add2",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.addlabel2",
        action_params={
            "port": ports[0],
            "flag": ports[1],
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel2 rule on %s" % ingress_sw.name

def writeTunnelRules3(p4info_helper, ingress_sw, egress_sw,
                     dst_eth_addr, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.ipv4_final",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.dmac",
        action_params={
            "hdr.ethernet.dstAddr":dst_eth_addr
        })
    egress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule3 on %s" % ingress_sw.name

def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print

def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print "%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            )

def printGrpcError(e):
    print "gRPC Error:", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    traceback = sys.exc_info()[2]
    print "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)














if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/source.routing_ipv4forward.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print
        "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print
        "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)