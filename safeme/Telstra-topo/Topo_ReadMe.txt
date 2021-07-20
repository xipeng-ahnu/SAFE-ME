1. In Telstra topology, there are 8 switches, each connected to 2 hosts. 
   There are 9VNF, including 3 Firewall, 3 IDS, 3 Proxy.
   All switches in the topology picture v1 ~ v8 are replaced to s1 ~ s8

2. We use the name mapping below to construct the whole network
F1 - s9
F2 - s10
F3 - s11

I1 - s12
I2 - s13
I3 - s14

P1 - s15
P2 - s16
P3 - s17

3. Each Switch sx has two hosts connected directly, named hx1, hx2

   for hxk, its ip address is 10.0.x.k/24, mac address is 80:00:00:00:0x:xk
   
   for hxk, its default route is 10.0.x.x0, default route mac is 80:00:00:00:0x:00
            this mac and ip is supposed to be the switch internal ip and mac which the host is directly connected
