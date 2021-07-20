/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_SAFEME = 0x0123;
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/
// the Ethernet Header Type for SAFE-ME is set to 0x0123
// for the reason that type from 0x0101 - 0x01FF are used for expermimental use


typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header safeme_t{
    bit<32> tagStorageField; // store the unprocessed NF tags
    bit<8> tagMatchField;    // store the current NF to be processed
    bit<16> preservedEtherType;  // store the Ether Type from the upper layer header
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

struct headers {
    ethernet_t   ethernet;
    safeme_t     safeme;
    ipv4_t       ipv4;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

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
            TYPE_SAFEME: parse_safeme;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_safeme {
        packet.extract(hdr.safeme);
        transition select(hdr.safeme.preservedEtherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
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
    /*********************** Actions Definition *************************/
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action myNoAction(){
    }

    // this action is for intermediate switch which is directly connected to the next NF and who needs to do shift forwarding
    action safeme_shift_forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.safeme.tagMatchField = (bit<8>)(hdr.safeme.tagStorageField); //get next tag and filled into tag match field
        hdr.safeme.tagStorageField = hdr.safeme.tagStorageField >> 8;  // right shift tag storage field 8 bits
        standard_metadata.egress_spec = port; // using tag to determine egress port
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // this action is for intermediate switch which is NOT directly connected to the next NF and who needs to do normal forwarding
    action safeme_normal_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port; // using tag to determine egress port
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // this action is for the switch that first see a valid safeme tag with match field all 0s
    // which means the safeme header is no need and goes to the basic forwarding process 
    action safeme_removetag(macAddr_t dstAddr, egressSpec_t port) {
        hdr.safeme.tagMatchField = 8w0;   // before invalid this header, every bit set to 0 for tag match and storage fields
        hdr.safeme.tagStorageField = 32w0;
        hdr.ethernet.etherType = hdr.safeme.preservedEtherType; // re-gain the ethertype from preserved to original ethernet type field
        hdr.safeme.setInvalid();
        standard_metadata.egress_spec = port; // using tag to determine egress port
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // this action is for the first switch to add safeme tag for the packet
    // the switch will look-up in the SFC table first to determine what tags needs to be add into the safeme header
    // then the switch preserve ethertype from ethernet header to the safeme header - preservedEtherType field for tag remove
    action safeme_addtag(bit<32> sTag, bit<8> mTag) {
        hdr.safeme.setValid();
        hdr.safeme.tagMatchField = mTag;
        hdr.safeme.tagStorageField = sTag;
        hdr.safeme.preservedEtherType = hdr.ethernet.etherType;
        hdr.ethernet.etherType = TYPE_SAFEME;
    }

    // if the safeme header field "tagMatchField" == 0x00
    // this means the packet finished all NFs, the rest forwarding path is like a normal packet
    // we just do nothing and let it go to the normal table matching
    // so this action is the same as NoAction in <core.p4>
    // in the control block, we just use if statement to judge whether tagMatchField == 0x00 or not
    // so this action can be omitted.
    /*
    action safeme_ipv4_forward() {
        //do nothing
    }
    */

     
    // Normal ipv4 forward
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    
    /**************************** Tables Definition ***********************************/
    
    /**************************** SAFE-ME SFC Table *********************************** 
     * safeme_sfc table is for matching normal ip packet without safeme header
     * if the packet hits the table, corresponding SFC tag will be filled into a new safeme header and adds to the packet after ethernet header
     * the packet original ethernet header field "etherType" will copy to the new safeme header field "preservedEtherType"
     * after this, the packet ethernet header field "etherType" will be set to the value "0x0123" to indicate the new safeme header is added
     * however, the safeme_sfc header only cares about ADD tag, remove the tag is not the duty of this table
     * if the packet miss this table, NO ACTION will be done, the packet remain unchanged and goes to the original pipeline process, ie. goes to ipv4 matching
     * when a new safeme header is added, it will goes to safeme_nf table for the next matching 
     */
    table safeme_sfc {
        key = {
            hdr.ipv4.srcAddr: lpm;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            safeme_addtag;
            myNoAction;
        }
        size = 4096;
        default_action = myNoAction();
    }
    /***************  SPECIAL CASE WARNING!!! ****************
     * After treated by safeme_sfc table, one packet may has a new safeme header to indicate its SFC rules
     * When the packet finishes going through all the NFs, safeme header field tagMatchField and tagStorageField will be all 0s
     * This means the safeme header is no use from this moment on! 
     * BUT, to distinguish from normal packet, we will keep the safeme header until the packet reached the egress switch to the host!
     * This method ensures a packet will never be treated wrong for adding SFC rules for a second time 
     */


    /***************************  SAFE-ME NF Table ********************
     * safeme_nf table is used for safeme header matching
     * when a packet has a safeme header, its tagMatchField will be checked, followed by three situations:
     * 1) the packet safeme header field tagMatchField matches a certain tag key, then it will find an output port towards the current NF which is identified by the tag key; if the switch is directly connected to the NF, it will also do the tag shift operation to change the tagMatchField for the next NF. This means the packet hit this table will be forwarded without change itself (safeme normal forward) OR shift tagMatchField and-then forward(safeme shift forward)
     * 2) the packet safeme header field tagMatchField missed the table matching process, BUT its value is not 0x00, this indicates a wrong NF tag key, in this program, we just DROP IT. Ofcouse we can also send it to the CONTROLLER as well.
     * 3) the packet safeme header field tagMatchField is 0x00, this indicates the packet has passed through all the NFs it should go, all the path left is normal forwarding. Then, we check if this is the last egress switch for this packet to its destination host. If it is, we remove the safeme header(BY safeme_removetag ACTION) and forward it to the host; If not, we just do nothing but let it go to normal pipeline process, ie: ipv4 header matching.
     */
    table safeme_nf {
        key = {
            hdr.safeme.tagMatchField: exact;
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            safeme_shift_forward;
            safeme_normal_forward;
            safeme_removetag;
            myNoAction;
            drop;
        }
        size = 1024;
        default_action = drop(); // here is a problem to be fixed, default_action should be drop, but in our experiment, we use switches to simulate NFs, so the NF like switch should mirror back every packet, it can not drop any packet even it contains a wrong tag in the safeme header, so in the controller script, we set safeme_nf table default_action = myNoAction for these NF like switches
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            myNoAction;
        }
        size = 1024;
        default_action = drop();
    }
    

    /*********************** Control Pipeline *********************/
    /*
     * README: The main packet process pipeline introduction
     * 1) Packets are classified by safeme header exists or not into two classes; 
     *     class A: normal packet without safeme header
     *     class B: normal packet with safeme header
     * 2) Towards class A packets, it must goes through safeme_sfc table fisrt looking for the SFC rules to ADD;
     *     Case 1: New safeme header added, then goes to safme_nf table to find output port for the current NF;
     *     Case 2: New safeme header added, and the NF is direct connect to this switch, then do shift operation and forward to NF
     *     Case 3: safeme_sfc table miss, do nothing, goes to ipv4_lpm table for normal forwarding
     * 3) Towards class B packets, it does not need to go through the safeme_sfc table, direct goes through safeme_nf table;
     *     Case 1: hit the table , judge whether need shift operation(BY Controller populated rules), forward to the NF;
     *     Case 2: table miss && tagMatchField is NOT 0x00, means tag wrong, drop it(this program choose) or send to Controller;
     *     case 3: table miss && tagMatchField is 0x00(this can be judged in the control codes), do safeme ipv4 packet forwarding
     */

    apply {
        if(!hdr.safeme.isValid()){ // class B packet
            safeme_sfc.apply();            
        }

        if(hdr.safeme.isValid()){ // new safeme header ADDED or the packet ALREADY has safeme header
            safeme_nf.apply();
        }else{ // class A packet and not hit the SFC table 
               // do normal ipv4 forward without safeme header, means a normal packet
            if (hdr.ipv4.isValid()) {
                ipv4_lpm.apply();
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
        packet.emit(hdr.safeme);
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
