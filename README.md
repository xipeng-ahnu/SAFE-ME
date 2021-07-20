# Experiment Enviroment For Implementing and Testing SAFE-ME Scheme with P4 Software Switches

## 1. Introduction
**This repository stores [P4](https://p4.org/) based implementation of SAFE-ME scheme and a reproducible experiment environment constructed on P4 supported [Mininet](http://mininet.org/).** 

The SAFE-ME scheme is a **Service Function Chaining Routing scheme** support policy enforcement. It is first proposed in our ICNP'19 work: [SAFE-ME paper](https://ieeexplore.ieee.org/document/8888123) . It is flexible and scalable for SDN-based middle-box networks. 

At the beginning, SAFE-ME was implemented in an OpenFlow-based SDN data plane with the help of MPLS header. Later, we received valuable suggestions that P4 based data plane will be more suitable for SAFE-ME. Thus, we augment the SAFE-ME design with P4 and perform experiment in our lab with physical servers. The outcomes prove that:

1. SAFE-ME can conveniently settled down into P4 based data plane and the correctness is ensured.

2. By testing and comparing the performance of SAFE-ME with other two schemes: PDA and SIMPLE in the Telstra topology, the results are very similar with our ICNP'19 work, which proves the sounding performance of SAFE-ME. 

**Here, we want to give special thanks to the reviewers who shepherd us to P4.**

## 2. P4 Implementation Details

### 2.1 Forwaring pipelines:
According to our paper, the SAFE-ME scheme use two different forwarding pipeline:

#### A) Basic forwarding pipeline: 
Use traditional IPv4 forwarding for packets which are no need to go through middle-boxes(NFs), 
the switch must perform the following actions for every packet: 
(i) update the source and destination MAC addresses,
(ii) decrement the time-to-live (TTL) in the IP header, and 
(iii) forward the packet out the appropriate port.
This type of pipeline only need an ip based matching table.
 
#### B) Service Function Chaining(SFC) forwarding pipeline:
First, we introduced a **new SAFE-ME header**
```
header safeme_t{
    bit<32> tagStorageField; // store the unprocessed NF tags
    bit<8> tagMatchField;    // store the current NF to be processed
    bit<16> preservedEtherType;  // store the Ether Type from the upper layer header
}
```
The SAFE-ME header is added in between ethernet header and ipv4 header. **A packet equipped with a SAFE-ME header will have a ethernet header with the etherType field set to a fixed experimental value: "*0x0123*".**

**The new 16 bits header field "*preservedEtherType*" is used to preserve the packet's original etherType value from the ethernet header.**

### 2.2 SAFE-ME P4 Matching Tables:

To implement SAFE-ME scheme, two matching tables are needed and introduced in our paper:

#### A) "*safeme_sfc*" Table:
When a packet is sent from a host to the ingress switch, it check this table to determine whether this packet needs to go through a SFC or not. If the packet needs to do so, the following actions will be taken sequencially:
 **Step 1.** filled the "tagStorageField" and "tagMatchField" in a new SAFE-ME header.
 **Step 2.** copy the packet's original etherType value to "preservedEtherType" field.
 **Step 3.** set the ethernet header field etherType with value "*0x0123*" and make the SAFE-ME header "*valid*".

 The *safeme_sfc* table is defined as below:
 ```
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
 ```

#### B) "*safeme_nf*" Table:
After a packet went over the *safeme_sfc* table, if the packet has a SAFE-ME header, it will go to match *safeme_nf* table. 

The *safeme_nf* table is defined as below:
 ```
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
        default_action = drop();
 }
 ```

 this table look up the tagMatchField to match the next NF and select an action in below:
 **- "*safeme_normal_forward*" Action:** the packet is going to the next NF and current switch is not the one closest to it, we only need to forward it through certain port.
 
 **- "*safeme_shift_forward*" Action:** the packet is going to the next NF and current switch is the closest one, we shift the tag as our paper described for matching the next NF. 
 The tag shifting operation codes are as below:	
  ```
  hdr.safeme.tagMatchField = (bit<8>)(hdr.safeme.tagStorageField);
  hdr.safeme.tagStorageField = hdr.safeme.tagStorageField >> 8;
  ```
Then, the switch sends it to the NF directly connected to it.
 
 **- "*safeme_removetag*" Action:** the packet is now at the egress switch closest to the destination host, we will first recover the etherType field in the ethernet header from the preservedEtherType field in the SAFE-ME header, then we will remove the SAFE-ME header in order to make the packet be the same as the source host sends. At last, we send it to the destination host.

## 3. Running the experiment:
In our lab, we use several servers and high-end workstations to build the experiment enviroment:
 - We run each P4 software switch on a Ubuntu 16.04 server with Xeon Gold 6152 processor and 128GB of RAM, as 8 servers in total.
 - Each NF is installed on a high-end workstation with Intel Core i9-10900 processor and 64GB of RAM, as 9 workstations in total.
 - Each host with Intel Core i5-10400 processor and 16GB of RAM, as 16 PCs in total.
 - A controller is deployed with a Ubuntu 16.04 server with Xeon Gold 6152 processor and 128GB of RAM, using gRPC protocol to send flow entries and control the data plane.
 
To help anyone interests with SAFE-ME and wants to reproduce our experiment, here we consolidate all the hardware and softwares into a Mininet implementation with the same SAFE-ME design and the same network topology - *Telstra* showed in our paper. We also implemented PDA and SIMPLE here, too. The flow entries sent by the controller had been written into files for pre-installing into the switches when they are at initialization process. Thus, the controller is omitted for simplicity.

** Please follow the steps here to run the expermiment network and do any test you want:**

### 3.1  P4 Enviroment and Dependencies Installing: 
Install P4 enviroment follow the [install-p4dev-v2.sh](https://github.com/jafingerhut/p4-guide/bin/install-p4dev-v2.sh) script in [P4-GUIDE](https://github.com/jafingerhut/p4-guide) in Ubuntu16.04.7 or Ubuntu18.04.

You will need to install [bmv2](https://github.com/p4lang/behavioral-model), [p4c](https://github.com/p4lang/p4c), [protobuf](https://github.com/google/protobuf), [grpc](https://github.com/google/grpc) and [p4runtime](https://github.com/p4lang/p4runtime). Specially, when you are installing *bmv2*, make sure to configure and install <font color="#dd0000">*simple_switch_grpc*</font> in the sub directory [./targets/simple_switch_grpc/](https://github.com/p4lang/behavioral-model/targets/simple_switch_grpc/).

### 3.2 Install Mininet
Please follow the guide from [mininet.org](https://mininet.org/) to install Mininet 2.3.0.


### 3.3 Create and run the experiment network based on *Telstra* topology with SAFE-ME or other benchmarks
#### Step 1: Git clone this repository
 Use ***git clone*** command to pull all the content of this repository to your PC or Laptop, with a certain directory, here we call it {YOUR GIT DIR}.

#### Step 2: Build the Network
In your Ubuntu shell command prompt, enter the directory "{YOUR GIT DIR}/safemeSim/safeme/". **Then you choose one of the shell commands below to run one scheme among SAFE-ME, PDA or SIMPLE:**
 
  ***make run***
   
   This will run the whole Telstra topology in mininet with SAFE-ME scheme enabled.

  ***make -f MakefileTelstra-PDA run***

   This will run the whole Telstra topology in mininet with PDA scheme enabled.

  ***make -f MakefileTelstra-simple run***

   This will run the whole Telstra topology in mininet with SIMPLE scheme enabled.

#### Step 3: Do tests or experiments
After one of the above command, you will find a mininet shell running.

Then you can use "***xterm h11***" or "***xterm h82***" to open new terminals with certain host. This will open one or several new command prompts.

In the new command prompt, you can use testing tools like [pktGen](https://github.com/netoptimizer/network-testing/pktgen/), [iperf3](https://iperf.fr/), [Qperf](https://pkgs.org/download/qperf) and so on to do any test your want.

Here, each switch is connected to 2 hosts. 
*S1* is connected with *h11* and *h12*. 
*S2* is connected with *h21* and *h22*.
......
*S8* is connected with *h81* and *h82*.

#### Step 4: Stop and Clean up

After the experiment, use the shell command below to stop the experiment:

***make stop***

Use the shell command below to stop the experiment and clean up the generated files:

***make clean***

## 4. Licenses and Credits
### 4.1 Licenses
Our programs and codes obeys the [Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).


### 4.2 Credits

The SAFE-ME scheme and programs are developed by **Intelligent Network and System Research Group** of Suzhou Institute for Advanced Study, University of Science and Technology of China, Suzhou, Jiangsu, China, 215123.

**Thanks to use our P4-based SAFE-ME scheme and the experiment code!**

## 5. Appendix

### 5.1 The large scale simulation code

We add our former simulation code in the directory "largeScaleSim".

### 5.2 The flow trace file

We store the flow trace file (pcap) in the directory "trafficTrace", which was once stored on the [dropbox](https://www.dropbox.com/s/f6wl5zyyfmqq4ry/flow_trace.pcap?dl=0)

