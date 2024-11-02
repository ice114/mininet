/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

// NOTE: new type added here
const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_REGI = 0x1234;
const bit<16> TYPE_ASK  = 0x1256;
const bit<16> TYPE_ANS = 0x1278;
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<16> dst_id_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;

}

// NOTE: added new header type

header myTunnel_t {
    ip4Addr_t t_src ;
    ip4Addr_t t_dst;
    bit<16> type;
}

header user_regi_t {
    ip4Addr_t u_srcIP;
    bit<16> longitude;
    bit<16> lagitude;
    ip4Addr_t dst_satIP;
}

header user_ask_t{
    ip4Addr_t u_srcIP;
    bit<16> longitude;
    bit<16> lagitude;
    ip4Addr_t dst_IP;
    ip4Addr_t dst_satIP;
}
header dcs_ans_t{
    bit<16> u_longitude;
    bit<16> u_lagitude;
    ip4Addr_t dst_IP;
    bit<16> d_longitude;
    bit<16> d_lagitude;
    ip4Addr_t dst_satIP;
}
header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    /* empty */
}

// NOTE: Added new header type to headers struct
struct headers {
    ethernet_t   ethernet;
    myTunnel_t   myTunnel;
    user_regi_t  myRegi;
    user_ask_t   myAsk;
    dcs_ans_t   myAns;
    ipv4_t       ipv4;

}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

// TODO: Update the parser to parse the myTunnel header as well
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition parse_ipv4;

    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ethernet.etherType) {
            TYPE_MYTUNNEL : parse_myTunnel;
	        TYPE_REGI:parse_myRegi;
	        TYPE_ASK:parse_myAsk;
	        TYPE_ANS:parse_myAns;
            default : accept;
        }
    }
    state parse_myRegi {
        packet.extract(hdr.myRegi);
        transition accept;
    }
    state parse_myAsk {
        packet.extract(hdr.myAsk);
        transition accept;
    }
    state parse_myAns {
        packet.extract(hdr.myAns);
        transition accept;
    }
    state parse_myTunnel{
        packet.extract(hdr.myTunnel);
 	    transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }


    action fillin_n_Tunnel_ingress(ip4Addr_t first_satIP,ip4Addr_t DCS_satIP){
        if(hdr.myRegi.isValid()){
            hdr.myRegi.dst_satIP = DCS_satIP;
        }else if(hdr.myAsk.isValid()){
            hdr.myAsk.dst_satIP = DCS_satIP;
        }else if(hdr.myAns.isValid()){
            hdr.myAns.dst_satIP = DCS_satIP;
        }
        hdr.myTunnel.setValid();
        hdr.myTunnel.t_src = first_satIP;
        hdr.myTunnel.t_dst = DCS_satIP;
        hdr.myTunnel.type = hdr.ethernet.etherType;
        hdr.ethernet.etherType = TYPE_MYTUNNEL;
    }

    table acc_filling{
        key = {
            hdr.ethernet.etherType:exact;
            hdr.ipv4.dstAddr:lpm;
        }
        actions ={
            fillin_n_Tunnel_ingress;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    action myTunnel_forward(egressSpec_t port, macAddr_t dstAddr){
        standard_metadata.egress_spec = port;
        hdr.ethernet.dstAddr=dstAddr;
    }

    action myTunnel_egress(egressSpec_t port, macAddr_t dstAddr) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.dstAddr=dstAddr;
        hdr.ethernet.etherType=hdr.myTunnel.type;
        hdr.myTunnel.setInvalid();
    }

    table myTunnel_exact{
        key = {
            hdr.myTunnel.t_src :exact;
            hdr.myTunnel.t_dst: exact;

        }
        actions = {
            myTunnel_forward;
            myTunnel_egress;
            drop;
        }
        size = 1024;
        default_action = drop();
    }



    apply {
        if (!hdr.myTunnel.isValid()) {
            acc_filling.apply();
        }
        if (hdr.myTunnel.isValid()){
            myTunnel_exact.apply();

        }

    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.myTunnel);
        packet.emit(hdr.myRegi);
        packet.emit(hdr.myAsk);
        packet.emit(hdr.myAns);


    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
