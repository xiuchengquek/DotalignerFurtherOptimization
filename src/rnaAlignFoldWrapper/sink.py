
__author__ = 'xiuchengquek'



import zmq
import sys
from progressbar import ProgressBar , Percentage, Bar, RotatingMarker, ETA
import os
import argparse




receiver_ip = "tcp://*:5558"
context = zmq.Context()
# Get reciever
receiver = context.socket(zmq.PULL)
receiver.bind(receiver_ip)
prg_bar = ProgressBar(widgets=[Percentage(), Bar(marker=RotatingMarker()), ETA()])
i = 0

if not os.path.exists('data/logs'):
    os.makedirs('data/logs')


if __name__ == '__main___':
    parser = argparse.ArgumentParser(description= " Sinker for ventalitor")
    parser.add_argument('-r', '--receiver', help=' port to listen to' )
    args = parser.parse_args()


    receiver_ip = "tcp://*:" + args.receiver
    context = zmq.Context()

    receiver_ip = args.vent
    sinker_ip = args.sinker
    context = zmq.Context()

    # Get reciever
    receiver = context.socket(zmq.PULL)
    receiver.connect(receiver_ip)

    prg_bar = ProgressBar(widgets=[Percentage(), Bar(marker=RotatingMarker()), ETA()])
    i = 0

    fh_out = open('data/logs/completed_rna_dist.log','w+')
    while True:
        msg = receiver.recv_json()
        if msg['sender'] == 'ventilator':
            total = int(msg['body'])
            prg_bar.maxval = total
            prg_bar = prg_bar.start()
        else:
            i += 1
            prg_bar.update(i)
            fh_out.write('%s\n'  % msg['body'])
        if total == i :
            break

    prg_bar.finish()
    fh_out.close()
