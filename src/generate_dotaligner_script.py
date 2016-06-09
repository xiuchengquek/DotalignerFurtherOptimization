


import argparse
from dotalignerWrapper.dotalignerWrapper import DotAlignerGrouped
from dotalignerWrapper.parameterFileParser import parse_param_file, parse_pairwise_alignments


parser = argparse.ArgumentParser(description='Dotaligner Wrapper - Current only print bash scripts ')

parser.add_argument('-s' , '--seq' , help = "pairwise alignment list")
parser.add_argument('-p' , '--para' , help = "parameter files")
parser.add_argument('-d' , '--dotaligner', help = 'path to the dotaligner')








if __name__ == '__main__' :
    args = parser.parse_args()
    parameters = parse_param_file(args.para)
    pairs =  parse_pairwise_alignments(args.seq)
    dotaligner = args.dotaligner
    da = DotAlignerGrouped(dotaligner, 'src/dotaligner_shell_scripts/')
    da.add_pairs(pairs)
    da.add_prefix_pairs('data/ps')
    da.update_parameters(parameters)
    da.generate_and_run()




