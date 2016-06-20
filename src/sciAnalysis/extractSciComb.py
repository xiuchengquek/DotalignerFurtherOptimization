#!/usr/bin/env python



import os
import argparse
import csv
from collections import OrderedDict


class sciEntry:
    def __init__(self, sequence_a, sequence_b, sci, is_diff=False):
        self.sequence_a = sequence_a
        self.sequence_b = sequence_b
        self.id = "%s %s" % (self.sequence_a,  self.sequence_b)
        self.sci = float(sci)
        self.is_diff = is_diff

    @classmethod
    def from_string(cls, string):
        values = string.split('\t')
        sequence_a = cls.clean_sequence_name(values[0])
        sequence_b = cls.clean_sequence_name(values[1])
        sci = float(values[-1])
        entry = cls(sequence_a, sequence_b, sci)
        return entry

    @classmethod
    def from_reference(cls, reference_file):
        results = []
        with open(reference_file) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                results.append(cls(row['SequenceA'] , row['SequenceB'],row['SCI'] ))
        return results

    @staticmethod
    def clean_sequence_name(sequence_name):
        sequence_name = os.path.basename(sequence_name)
        sequence_name = sequence_name.replace('_dp.pp', '')
        return sequence_name

    @staticmethod
    def get_parameters(filename):
        params = os.path.basename(filename)
        params = params.replace('.dotaligner.out.sci', '')
        params = params.split('_')
        params_ordered = OrderedDict()
        for x in params:
            key, value= x.split('-')
            params_ordered[key] = value
        return params_ordered


    def __str__(self):
        return "%s\t%s\t%.6f" % (self.sequence_a, self.sequence_b, self.sci)

    def to_string(self):
        return self.__str__()

    def __sub__(self, other):


        if (self.id != other.id):
            raise ValueError('Subtracting with non-reference pair')


        diff = self.sci - other.sci
        return sciEntry(self.sequence_a, self.sequence_b, diff, True)





def read_and_find(reference, dotaligner):
    reference_sci = sciEntry.from_reference(reference)
    reference_sci = {x.id : x for x in reference_sci}
    parameters = sciEntry.get_parameters(dotaligner)

    results  = []
    outname = "%s.diff" % dotaligner

    with open(dotaligner, 'r') as f:
        next(f)
        for line in f:
            line = line.strip()
            sci_obj = sciEntry.from_string(line)
            ref_obj = reference_sci[sci_obj.id]
            sci_diff = sci_obj - ref_obj
            results.append(sci_diff)
    combinations = parameters.values()
    combinations = list(combinations)
    combinations = [str(x) for x in combinations]
    with open(outname, 'w+') as f:
        f.write("%s\tSequenceA\tSequenceB\tsci-diff\n" % "\t".join(list(parameters.keys())))
        for x in results:
            f.write("%s\t%s\n" % ("\t".join(combinations), x.to_string()))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add combination and find difference between sci - refsci')
    parser.add_argument('-r', '--ref' ,help="reference score")
    parser.add_argument('-s', '--sci' ,help='sci file')
    args = parser.parse_args()
    read_and_find(args.ref, args.sci)


