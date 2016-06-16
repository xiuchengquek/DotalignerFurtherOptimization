__author__ = 'xiuchengquek'


import os
import sys
import json
import zmq

import argparse





def load_sample_list(directory):
    dotaligner_output = os.listdir(directory)
    dotaligner_output = [ x for x in dotaligner_output if x.endswith('dotaligner.out') ]
    dotaligner_output = [ os.path.join(directory, x) for x in dotaligner_output ]
    return dotaligner_output


if __name__ == '__main__' :

    parser = argparse.ArgumentParser(description='Please PLce sinker and worker port')
    parser.add_argument('-w', '--worker' ,help="worker port")
    parser.add_argument('-s', '--sinker' ,help='sinker ip')
    parser.add_argument('-i', '--dotdir', help='dotaligner folder')
    parser.add_argument('-o', '--output' , help='output file')
    args = parser.parse_args()

    context = zmq.Context()
    reciever_id = 'tcp://*:' + args.worker
    sink_ip = args.sinker

    # Get reciever
    sender = context.socket(zmq.PUSH)
    sender.bind(reciever_id)

    sinker = context.socket(zmq.PUSH)
    sinker.connect(sink_ip)

    samples_list = load_sample_list(args.dotdir)


    sinker.send_json({
        'sender' : 'ventilator',
        'body' : ";".join(samples_list)
    })

    for x in samples_list:
        sender.send_json({ 'sample' : x })


