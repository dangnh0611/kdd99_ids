#!/usr/bin/env python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node,Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled, act like a router."
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):
    "A simple simulated office network."
    def build( self, n1, n2 ):
        defaultIP = '192.168.2.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip= defaultIP )
        s1, s2, s3, s4 = [ self.addSwitch( s) for s in ( 's1', 's2', 's3', 's4') ]
        self.addLink( s2, router, cls=TCLink, bw=20, delay='1ms', intfName2='r0-eth1', params2={ 'ip' : defaultIP } )
        self.addLink( s1, router, intfName2='r0-eth2', params2={ 'ip' : '100.10.0.1/24' } )
        self.addLink(s3, s2)
        self.addLink(s4, s2)

        # DMZ zone contain 2 hosts
        h1 = self.addHost( 'h1', cpu=0.10,  ip='100.10.0.2/24', defaultRoute='via 100.10.0.1' )
        h2 = self.addHost( 'h2', cpu=0.10,  ip='100.10.0.3/24', defaultRoute='via 100.10.0.1' )
        self.addLink(h1, s1, cls=TCLink, bw=20, delay='1ms')
        self.addLink(h2, s1, cls=TCLink, bw=20, delay='1ms')

        # Internal zone
        # n1 host connect to switch s3
        for i in range(n1):
            host=self.addHost('h%s'%(i+3), cpu=0.2/n1, ip='192.168.2.%s/24'%(i+3), defaultRoute='via 192.168.2.1')
            self.addLink(host, s3, cls=TCLink, bw=15, delay='2ms' )
        # n2 host connect to switch s4
        for i in range(n2):
            host= self.addHost('h%s'%(i+ n1 + 3), cpu=0.2/n2, ip='192.168.2.%s/24'%(i+ n1 + 3), defaultRoute='via 192.168.2.1')
            self.addLink(host, s4, cls=TCLink, bw=15, delay='2ms')

def run():
    topo = NetworkTopo(3,3)
    net = Mininet(topo=topo, controller=None)
    c0 = net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6653)
    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    info('*** Starting some service')
    # ftp service
    net['h1'].cmd('sudo twistd -n ftp -p 21 -r /home/dangnh/ids &> /dev/null &')
    # http web service
    net['h1'].cmd('python -m SimpleHTTPServer 80 &> /dev/null & ')
    # ssh service
    net['h1'].cmd('/usr/sbin/sshd -D &')

    net['h2'].cmd('python -m SimpleHTTPServer 80 &> /dev/null & ')
    net['h2'].cmd('/usr/sbin/sshd -D &')

    info('*** Testing connection: \n')
    info(net.pingAll())

    info( '*** Running services on host h1:\n' )
    info(net['h1'].cmd('netstat -tulpn | grep LISTEN'))
    info( '*** Running services on host h2:\n' )
    info(net['h2'].cmd('netstat -tulpn | grep LISTEN'))

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

topos = { 'tp': ( lambda n1, n2 : NetworkTopo(n1, n2) ) }