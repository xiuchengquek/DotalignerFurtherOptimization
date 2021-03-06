#!/usr/bin/env python
__author__ = 'xiuchengquek'

import sys
import time

import argparse
from rnaFoldRunner import read_and_run
import zmq


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= " Worer for RNAAlign + ClustalW. Enter listen port and sinker ip")
    parser.add_argument('-s', '--sinker', help=' sinkerip' )
    parser.add_argument('-v', '--vent', help="vent ip")
    args = parser.parse_args()

    reciever_ip =  args.vent
    sinker_ip = args.sinker
    context = zmq.Context()

    # Get reciever
    receiver = context.socket(zmq.PULL)
    receiver.connect(reciever_ip)

    sinker = context.socket(zmq.PUSH)
    sinker.connect(sinker_ip)
    while True:
        data = receiver.recv_json()
        sample = data['sample']
        read_and_run(sample)
        sinker.send_json({
            'sender' : 'worker',
            'body' : "%s\tcompleted" % sample
        })

