import os
from src.sciAnalysis import extractSciComb


dotaligner_out_folder = 'out/dotaligner_out'
sci_files = os.listdir(dotaligner_out_folder)
sci_files = [os.path.join(dotaligner_out_folder, "%s.diff" % x) for x in sci_files]

rule all :
    input: sci_files


rule run_sci_diff_analysis:
    input : sci = dotaligner_out_folder  + '/{sample}.sci'  , ref = 'data/reference_sci.csv'
    output : dotaligner_out_folder + '/{sample}.sci.diff'
    shell : 'python src/sciAnalysis/extractSciComb.py -r {input.ref} -s {input.sci}'