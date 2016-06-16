__author__ = 'xiuchengquek'


import os
import subprocess
import re
import tempfile
import sys

MEFSCORERE = re.compile('.*\(([\s\-0-9\.]+)\)\\\\n\'')



def run_rna_fold(sequence):
    """
    This function serves to run rnafold and get the MFE score using regular expression
    :param sequence: string containing sequence
    :return score: float contain MFE score of aligned sequences
    """
    sequence = sequence.replace('-', '')
    sequence = str.encode(sequence)
    cmd = ['RNAfold']

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    try :
        outs, errs = p.communicate(input=sequence,timeout=600) # set time out, should finish in 600secs

    except TimeoutError:
        p.kill()
        outs, errs = p.communicate()

    ## will throw array if fails
    result = str(outs)
    score = MEFSCORERE.search(result).group(1)
    score = float(score)


    return score


def read_and_run(filename):
    """
    This is the main function for running the jobs. It takes in a results file and generate 2 ouptut file. an error and
    a result file
    :param filename: filename of results from dot aligner
    :return: fh_out: writes a file with suffix sci contain sci_score of each pair of alignment
    :return: err_filename: writes a file with suffix err. contains information about alignments withe error
    """

    output_filename = "%s.sci" % filename
    err_filename = "%s.err" % filename

    fh_out = open(output_filename, 'w+')
    fh_out.write('SequenceA\tSequenceB\tSequenceA_MFE\tSequenceB_MFE\tAln_MFE\tAln_MFE_Raw\tAln_MFE_offset\tSCI\n')

    fh_err = open(err_filename, 'w+')

    with open(filename, 'r') as f:
        for line in f:
            try :
                stripped_line = line.strip()
                fields = stripped_line .split('\t')
                # get sequences
                seq_a = fields[6]
                seq_b = fields[8]
                # get names
                seq_name_a = fields[0]
                seq_name_b = fields[1]
                # get mfe score
                mfe_a = run_rna_fold(seq_a)
                mfe_b  = run_rna_fold(seq_b)
                # generate clustalW
                temp_file_name = generate_clustalW(seq_a, seq_b)
                # run rnaali
                score = run_rna_ali(temp_file_name)
                sci =  score[0] / ((mfe_a + mfe_b) / 2 )
                score = "\t".join([str(x) for x in score])
                output = [seq_name_a, seq_name_b, mfe_a, mfe_b, score, sci]
                output = "\t".join([ str(x) for x in output])
                fh_out.write("%s\n" % output)
                os.unlink(temp_file_name)
            except:
                fh_err.write(line)

    fh_err.close()
    fh_out.close()

def generate_clustalW(seq_a, seq_b):
    """
    This function create a temporary clustalW file for running rnaalifold.
    :param seq_a: String - first sequence of the pair
    :param seq_b: String - second sequence of the pair
    :return f.name: temporary name of clustalW file
    """
    f = tempfile.NamedTemporaryFile(delete=False)
    clusterStr = "CLUSTALW\n\n" + \
                 "SeqA\t%s\n" % seq_a + \
                 "SeqB\t%s\n" % seq_b

    f.write(str.encode(clusterStr))
    f.close()
    return f.name


def run_rna_ali(filename):
    """
    This function is a wrapper around rna_alifold and served to get the MFE score from the alignment
    :param filename:  the filename of the clustalW file
    :return: sci score
    """

    cmd = ['RNAalifold', filename]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    score = []
    try :
        outs, errs = p.communicate(timeout=600) # set time out, should finish in 600secs
        result = outs.decode('ascii')
        result = result.strip()
        result = result.split('\n')
        result = result[-1].split(' ',1)
        result = result[-1]
        result = result.replace('(', '')
        result = result.replace(')', '')
        score = re.split('[=\+]', result)
        score = [float(x.strip()) for x in score]
    except TimeoutError:
        p.kill()
        outs, errs = p.communicate()

    return score


def process_chain(sequence_pair):
    """
    This function is written mainly to help with the multiple processin module of python
    :param sequence_pair: tuple conatining dicatioary wiht information of both sequences.
    :return: output
    """
    seq_a = sequence_pair[0]
    seq_b = sequence_pair[1]
    mfe_a = run_rna_fold(seq_a['sequence'])
    mfe_b = run_rna_fold(seq_b['sequence'])
    clustalw_file = generate_clustalW(seq_a['sequence'], seq_b['sequence'])
    score  = run_rna_ali(clustalw_file)
    sci =  score[0] / ((mfe_a + mfe_b) / 2 )
    score = "\t".join([str(x) for x in score])
    output = [seq_a['file'], seq_a['name'], seq_b['name'], mfe_a, mfe_b, score, sci]

    output = "\t".join([ str(x) for x in output])
    return output






