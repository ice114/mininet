/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

// NOTE: new type added here
const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_REGI = 0x1234;
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
}

header user_regi_t {
    bit<16> regi_state;
    ip4Addr_t u_srcIP;
    bit<16> longitude;
    bit<16> lagitude;
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
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4 : parse_ipv4;
	    TYPE_MYTUNNEL : parse_myTunnel;
	    TYPE_REGI:parse_myRegi;
            default : accept;
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


    action myRegi_fillin(ip4Addr_t DCS_satIP){
        hdr.myRegi.dst_satIP = DCS_satIP;
        hdr.myRegi.regi_state= 1;
    }

    table myRegi_filling{
        key = {
            hdr.myRegi.regi_state:exact;
        }
        actions ={
            myRegi_fillin;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }


    action myTunnel_ingress(ip4Addr_t n_src) {
            hdr.myTunnel.setValid();
            hdr.myTunnel.t_src = n_src;
            hdr.myTunnel.t_dst = hdr.myRegi.dst_satIP;
            hdr.ethernet.etherType = TYPE_MYTUNNEL;
        }

    
    table ipv4_lpm {
        key = {
            hdr.myRegi.u_srcIP:lpm;

        }
        actions = {
            myTunnel_ingress;
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
        hdr.myTunnel.setInvalid();
        hdr.ethernet.etherType=TYPE_REGI;
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
        if (hdr.myRegi.isValid() && !hdr.myTunnel.isValid()) {
            myRegi_filling.apply();
            ipv4_lpm.apply();
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
        packet.emit(hdr.myTunnel);
        packet.emit(hdr.myRegi);
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
