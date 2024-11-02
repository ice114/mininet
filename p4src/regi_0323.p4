/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

// NOTE: new type added here
#define MAX_HOPS 9
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_SRCROUTING =0x1111;
const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<16> TYPE_REGI = 0x1234;
const bit<16> TYPE_ASK  = 0x1256;
const bit<16> TYPE_ANS = 0x1278;
const bit<9>  TYPE_ACCEPT = 1;
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
    bit<16> direction;
    ip4Addr_t u_srcIP;
    bit<16> longitude;
    bit<16> lagitude;
    ip4Addr_t dst_satIP;
}

header user_ask_t{
    bit<16> direction;
    ip4Addr_t u_srcIP;
    bit<16> longitude;
    bit<16> lagitude;
    ip4Addr_t dst_IP;
    ip4Addr_t dst_satIP;
}
header dcs_ans_t{
    bit<16> direction;
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
header srcRoute_t {
    bit<16>    bos;
    bit<16>   port;
}
struct metadata {
    /* empty */
}

// NOTE: Added new header type to headers struct
struct headers {
    ethernet_t   ethernet;
    srcRoute_t[MAX_HOPS]    srcRoutes;
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
        transition select(hdr.ethernet.etherType){
        TYPE_SRCROUTING: parse_srcRouting;
        TYPE_MYTUNNEL : parse_myTunnel;
	    TYPE_REGI:parse_myRegi;
	    TYPE_ASK:parse_myAsk;
	    TYPE_ANS:parse_myAns;

        }

    }
    state parse_srcRouting {
            packet.extract(hdr.srcRoutes.next);
            transition select(hdr.srcRoutes.last.bos) {
                1: parse_ipv4;
                TYPE_REGI:parse_myRegi;
                TYPE_ASK:parse_myAsk;
                TYPE_ANS:parse_myAns;
                default: parse_srcRouting;
            }
        }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
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


    action srcRoute_nhop() {
        standard_metadata.egress_spec = (bit<9>)hdr.srcRoutes[0].port;
        hdr.srcRoutes.pop_front(1);
    }

    action srcRoute_finish() {
        hdr.ethernet.etherType = hdr.srcRoutes[0].bos;
        if(hdr.myRegi.isValid()){
         hdr.myRegi.direction=2;
        }
        if (hdr.myAsk.isValid()){
        hdr.myAsk.direction=2;
        }
        if(hdr.myAns.isValid()){
            hdr.myAns.direction=2;
        }

    }

    action update_ttl(){
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    action accept_forward(){
        standard_metadata.egress_spec = TYPE_ACCEPT;
    }


    apply {
        if (hdr.srcRoutes[0].isValid()){
            if (hdr.srcRoutes[0].bos !=0){
                srcRoute_finish();
            }
            srcRoute_nhop();
            if (hdr.ipv4.isValid()){
                update_ttl();
            }
        }else{
            if(hdr.myRegi.isValid()){
                accept_forward();
            }else if (hdr.myAsk.isValid()){
                accept_forward();
            }
            else if (hdr.myAns.isValid()){
                accept_forward();
            }

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
        packet.emit(hdr.srcRoutes);
        packet.emit(hdr.myTunnel);
        packet.emit(hdr.myRegi);
        packet.emit(hdr.myAsk);
        packet.emit(hdr.myAns);
        packet.emit(hdr.ipv4);

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
