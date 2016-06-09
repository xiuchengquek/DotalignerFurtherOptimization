
import os
import subprocess
from collections import OrderedDict


class DotAlignerWrapper:
    def __init__(self, dotaligner_path):
        if os.path.exists(dotaligner_path):
            self.dot_aligner = dotaligner_path
        else :
            raise FileNotFoundError('dot_aligner not found at %s' % dotaligner_path)

        ## Default Parameters
        self.params_dict = {
            'e' : ['0.2'],
            'o' : ['1'],
            't' : ['0.5'],
            'k' : ['0.5'],
            'T' : ['1'],
            'S' : ['10'],
        }


    def add_pairs(self, pairs):
        self.pairs = pairs

    def update_parameters(self, params_dict):
        self.params_dict.update(params_dict)

    def add_prefix_pairs(self, prefix):
        self.prefix = prefix

    def get_combinations(self):
        for e in self.params_dict['e']:
            for o in self.params_dict['o']:
                for t in self.params_dict['t']:
                    for k in self.params_dict['k']:
                        for T in self.params_dict['T']:
                            for S in self.params_dict['S']:
                                 yield OrderedDict([ ('e' , e ),
                                 ('o' , o ),
                                 ('t' , t ),
                                 ('k' , k ),
                                 ('T' , T ),
                                 ('S' , S )])


    def generate_and_run(self):
        for parameters in self.get_combinations():

            for pairs in self.pairs:
                sequence_a , sequence_b = pairs
                if self.prefix:
                    sequence_a = os.path.join(self.prefix, sequence_a)
                    sequence_b = os.path.join(self.prefix, sequence_b)
                dotaligner_command = "(/usr/bin/time -f '\t%E\t%M' {dotaligner} -k {k} -t {t} -o {o}" \
                                     " -e {e} -s {S} -T {T} {sequence_a}_dp.pp {sequence_b}_dp.pp; ) >> out/k_{k}-t_{t}-o_{o}-e_{e}-T_{T}.dotaligner.out 2>&1".format(
                    dotaligner=self.dot_aligner,
                    k = parameters['k'],
                    t = parameters['t'],
                    o = parameters['o'],
                    e = parameters['e'],
                    S = parameters['S'],
                    T = parameters['T'],
                    sequence_a = sequence_a,
                    sequence_b = sequence_b)
                self.run_dotaligner(dotaligner_command, pairs, parameters)

    def run_dotaligner(self, command, pairs, parameters):
        print(command)

class DotAlignerSubprocess(DotAlignerWrapper):
    def run_dotaligner(self, command, pairs, parameters):
        subprocess.call(command, shell=True)

class DotAlignerZeroMQ(DotAlignerWrapper ):
    def run_dotaligner(self, command, pairs, parameters):
        pass


class DotAlignerDRMAA(DotAlignerWrapper):
    def run_dotaligner(self, command, pairs, parameters):
        pass

class DotAlignerGrouped(DotAlignerWrapper):

    def __init__(self, dotaligner_path, src_output=''):
        self.current_id = None
        self.command_list = []
        self.scr_output = src_output

        super().__init__(dotaligner_path)

    def generate_and_run(self):
        super().generate_and_run()
        with open(os.path.join(self.scr_output, self.current_id), 'w') as f:
            f.write("\n".join(self.command_list))



    def run_dotaligner(self, command, pairs, parameters):
        sample_name = []
        for key, value in parameters.items():
            sample_name.append(key)
            sample_name.append(value)
        sample_name = "_".join(sample_name)

        if self.current_id is None:
            self.current_id = sample_name

        if self.current_id == sample_name:
            self.command_list.append(command)
        else:
            with open(os.path.join(self.scr_output, self.current_id), 'w') as f:
                f.write("\n".join(self.command_list))
            self.current_id = sample_name
            self.command_list = []
            self.command_list.append(command)


















































