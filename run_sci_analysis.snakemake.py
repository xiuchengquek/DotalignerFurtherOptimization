import os
from src.sciAnalysis import extractSciComb


dotaligner_out_folder = 'out/dotaligner_out'
sci_files = os.listdir(dotaligner_out_folder)
sci_files = [os.path.join(dotaligner_out_folder, "%s.diff" % x) for x in sci_files if x.endswith('out.sci')]

rule all :
    input: sci_files, 'out/merged/seq.index.txt', 'out/merged/combination.index.txt', 'out/merged/merged_sci_diff.txt'

rule run_sci_diff_analysis:
    input : sci = dotaligner_out_folder  + '/{sample}.out.sci'  , ref = 'data/reference_sci.csv'
    output : dotaligner_out_folder + '/{sample}.out.sci.diff'
    shell : 'python src/sciAnalysis/extractSciComb.py -r {input.ref} -s {input.sci}'

rule create_indexes:
    input :sci_files
    output : com = 'out/merged/combination.index.txt' , out = 'out/merged/merged_sci_diff.txt', seq ='out/merged/merged/seq.index.txt'
    shell : 'python src/sciAnalysis/SciDiffAnalysis.py -d out/dotaligner_out -o {output.out} -c {output.com} -s {output.seq}'









