
import csv
import os
import argparse
from collections import OrderedDict
class SciDiffAnalysis:
    def __init__(self, directory, parameters):
        self.files = [os.path.join(directory, x) for x in  os.listdir(directory) if x.endswith('diff') ]
        self.combinations = OrderedDict()
        self.combination_counter = 0
        self.sequence_pair = OrderedDict()
        self.sequence_counter = 0
        self.parameters = parameters

    def read_and_count_write(self, outputfile):
        fh_out = open(outputfile, 'w')
        fh_out.write('combination\tsequence\tsci-diff\n')

        for x in self.files:
            with open(x, 'r') as f:
                reader = csv.DictReader(f, delimiter = '\t')
                for row in reader:
                    combination = self.get_combination(row)
                    sequence_pair = self.get_sequence_pair(row)
                    combination_index = self.add_to_combination(combination)
                    sequence_index = self.add_to_sequence_pair(sequence_pair)
                    fh_out.write("%s\t%s\t%s\n" % (combination_index, sequence_index, row['sci-diff']))
        fh_out.close()


    def write_combination(self, output):

        header = ['index' ]
        header.extend(self.parameters)
        header = "\t".join(header)

        with open(output , 'w') as f:
            f.write("%s\n" % header)
            for key, value in self.combinations.items():
                f.write('%i\t%s\n' % (value, key))


    def write_sequence(self, output):
        header = 'index\tSequenceA\tSequenceB\n'
        with open(output, 'w') as f:
            f.write(header)
            for sequence_pair, index in self.sequence_pair.items():
                f.write('%s\t%s\n' % (index, sequence_pair))


    def get_combination(self, row):
        combination  = []
        for x in self.parameters:
            combination.append(row[x])
        return "\t".join(combination)

    def get_sequence_pair(self, row):
        return "%s\t%s" % (row['SequenceA'], row['SequenceB'])


    def add_to_combination(self, entry):
        if entry not in self.combinations:
            self.combination_counter += 1
            self.combinations[entry] = self.combination_counter
        return self.combinations[entry]

    def add_to_sequence_pair(self,  entry):
        if entry not in self.sequence_pair:
            self.sequence_counter += 1
            self.sequence_pair[entry] = self.sequence_counter
        return self.sequence_pair[entry]



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine results and create index and combination map files")
    parser.add_argument('-d', '--dir' ,help="directory where diff files are found")
    parser.add_argument('-o', '--out' ,help='outfile')
    parser.add_argument('-s', '--seq' ,help='sequence index')
    parser.add_argument('-c', '--com' ,help='combination index')

    args = parser.parse_args()


    sci = SciDiffAnalysis(args.dir)
    sci.read_and_count_write(args.out)
    sci.write_sequence(args.seq)
    sci.write_combination(args.com)





