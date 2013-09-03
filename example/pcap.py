#!/usr/bin/python

from core.datastore import Datastore
from core.seriesprofile import SeriesProfile
from core.axis import Axis
from gui import Gui
import subprocess
import threading
import time

UNKNOWN_DAG = "unknown"
AVERAGING_INTERVAL = 10

class Node(object):
    def __init__(self, macaddr):
        self.macaddr = macaddr
        self.dag = UNKNOWN_DAG
        
    def setDag(self, dag):
        if self.dag != dag:
            self.dag = dag
            return True # DAG changed
        else:
            return False


class Dag(object):
    def __init__(self, address, series):
        self.address = address
        self.series = series
        self.byteCounter = 0


class PacketCounter(threading.Thread):
    def __init__(self, datastore):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.stopped = False
        self.nodes = {} # LAN stations indexed by MAC address
        self.dags = {}
        self.fieldbins = {}
        self.fields = ["frame.number", "frame.time_epoch", "frame.len", "frame.protocols",
                       "wpan.frame_type", "wpan.security",
                       "wpan.src64", "wpan.dst64", "icmpv6.type", "icmpv6.code",
                       "ipv6.src", "ipv6.dst", "6lowpan.fragment.count",
                       "icmpv6.rpl.dio.dagid", "icmpv6.rpl.dao.dodagid", "icmpv6.rpl.daoack.dodagid"]
        
    def startCapture(self):
        tshark = ["tshark", "-t", "e", "-T", "fields"]
        inputopts = ["-r", "/home/jonas/workspace/nowplot/longradio.pcap"]
        fieldopts = []
        for f in self.fields:
            fieldopts.append("-e")
            fieldopts.append(f)
        cmdline = tshark + inputopts + fieldopts
        print("Running %s" % " ".join(cmdline))
        
        self.process = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    
    def stop(self):
        self.stopped = True
        
    def run(self):
        self.startCapture()
        
        lastCommitTime = 0
        
        while not self.stopped:
            line = self.process.stdout.readline()
            if line == "":
                break
            items = line.rstrip("\n").split("\t")
            items = dict(zip(self.fields, items))
            #print(items)
            
            utc = float(items["frame.time_epoch"])
            
            # Keep some information about this node
            mac = items["wpan.src64"]
            if not mac in self.nodes:
                node = Node(mac)
                self.nodes[mac] = node
                print("%s Found node #%d: %s" % (time.ctime(utc), len(self.nodes), mac))
            else:
                node = self.nodes[mac]
            
            # Try to find out what DAG this node is in, and by extension its IP full address
            if items["icmpv6.rpl.dio.dagid"]: dag = items["icmpv6.rpl.dio.dagid"]
            elif items["icmpv6.rpl.dao.dodagid"]: dag = items["icmpv6.rpl.dao.dodagid"]
            elif items["icmpv6.rpl.daoack.dodagid"]: dag = items["icmpv6.rpl.daoack.dodagid"]
            else: dag = UNKNOWN_DAG
            
            if dag is not UNKNOWN_DAG:
                changed = node.setDag(dag)
                if changed:
                    print("%s %s changed DAG to %s" % (time.ctime(utc), mac, node.dag))
            else:
                dag = node.dag
                
            items["dag"] = dag

            # Count this packet in the DAG that this node belongs to
            if not dag in self.dags:
                series = self.datastore.addSeries(dag)
                self.dags[dag] = Dag(dag, series)
            self.dags[dag].byteCounter += int(items["frame.len"])
            
            # Add node statistics to out bins
            for field, value in items.iteritems():
                if field == "frame.number": continue
                if field == "frame.time_epoch": continue
                
                if not field in self.fieldbins:
                    self.fieldbins[field] = {}
                bins = self.fieldbins[field]
                if not value in bins:
                    bins[value] = 0
                bins[value] += 1
            
            # When we pass the averaging interval, commit the samples
            if utc > lastCommitTime + AVERAGING_INTERVAL:
                dt = utc - lastCommitTime
                for dag in self.dags.itervalues():
                    dag.series.addSample(utc, dag.byteCounter / dt)
                    dag.byteCounter = 0
                lastCommitTime = utc
            
        for field, bins in self.fieldbins.iteritems():
            print("%s:" % field)
            for bin, count in bins.iteritems():
                print("  %s: %3d" % (bin, count))


if __name__ == "__main__":
    datastore = Datastore()
    
    pc = PacketCounter(datastore)
    pc.start()
    
    gui = Gui(datastore, {
                    "fdc4:fffe:0:1:200:2000:2e:31": SeriesProfile(point=3, line=2, color="000000"),
                    "2008::1:200:2000:40:21": SeriesProfile(line=2, color="ff0000"),
                    "20dd::2:200:2000:36:34": SeriesProfile(line=2, color="00ff00"),
                    "2006::1:200:2000:34:19": SeriesProfile(line=2, color="0000ff"),
                    "20dd::1:200:2000:23:32": SeriesProfile(line=2, color="ffff00"),
                    "2108:0:47:29:200:2000:47:29": SeriesProfile(line=2, color="ff00ff"),
                    UNKNOWN_DAG: SeriesProfile(line=2, color="ffffff"),
                     })
    gui.getMainPlotWidget().setXAxis(Axis(0, 3600, wrap=True))
    gui.getMainPlotWidget().setYAxis(Axis(-50, 2000))
    gui.run()
