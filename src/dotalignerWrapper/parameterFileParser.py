import os

import sys




def parse_pairwise_alignments(file):
    pairs_list = []
    with open(file) as f:
        for line in f:
            fields = line.split('\t')
            pairs = fields[:2]
            pairs_list.append(pairs)
    return pairs_list

def parse_param_file(file):
    params_dict = {}
    with open(file) as f:
        for line in f:
            if not line.startswith('Parameters'):
                line = line.strip()
                parameters, values = line.split('\t')
                values = values.split(',')
                params_dict[parameters] = values
    return params_dict












