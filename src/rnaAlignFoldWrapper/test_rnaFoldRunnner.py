


import unittest
from unittest.mock import create_autospec, patch, Mock

import tempfile
from rnaFoldRunner import *


class simpleRunRNAFold(unittest.TestCase):

    def setUp(self):
        self.workingSeqA = 'ATTTGAGAGAGATCTATCGACTAGCTAG-TCGATCGATCGATGCTAGCTGACTGATCGATGCATGTAGAAATC'
        self.workingSeqNameA = 'SeqA'
        self.workingSeqB= 'ATTTGAGAGAGATCTATCGACTAGCTAGTC-GATCGATCGATGCTAGCTGACTGATCGATGCATGTAGAAATATTTGAGAGAGATCTATCGACTAGCTAGTCGATCGATCGATGCTAGCTGACTGATCGATGCATGTAGAAATCC'
        self.workingSeqNameB = 'SeqB'
        self.seqAMFE = -17.70
        self.seqBMFE = -52.00
        self.errorSeq = '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'



    def test_RunRNAFold_work(self):
        results = run_rna_fold(self.workingSeqA)
        self.assertEqual(results, self.seqAMFE)

    def test_RunRNAFold_workAandB(self):
        results = run_rna_fold(self.workingSeqA)
        self.assertEqual(results, self.seqAMFE)
        results = run_rna_fold(self.workingSeqB)
        self.assertEqual(results,self.seqBMFE)

    def test_RunRNAFold_fail(self):
        with self.assertRaises(AttributeError):
             run_rna_fold(self.errorSeq)



class simpleRunFromLine(unittest.TestCase):
    def setUp(self):
        self.clustalw_mfe = [-18.75, -17.75, -1.00]
        self.seqA = 'GCCUACGGCCAUACCACCCUGAAAG-CGC-CCGAUCU-CGUCU-GAUCUCGGAAGCUAAGCAGGGACGGGCUUGGUUAGUACCUGGAUGGGAGACCGCCUGGGAAUACCAGGU-GUUG-UAGGC'
        self.seqB = 'G--U-UGGUGAUUACAGAGAAAAGGUCACACUCAGCUCCAUUUCGAACCUGAAAGUUAAGC-UUUUC-UUCGUCGAUAAUA-CUGCCCCCUA-CGGGGGUGGG-ACGGUAGAUCGUUGCCAACC'

    def test_generateClustalW(self):
        file_name =  generate_clustalW(self.seqA, self.seqB)
        self.assertTrue(os.path.exists(file_name))
        os.unlink(file_name)


    def test_run_rnaFoldAli(self):
        file_name =  generate_clustalW(self.seqA, self.seqB)
        results = run_rna_ali(file_name)
        self.assertEqual(self.clustalw_mfe, results)
        os.unlink(file_name)


class readAndRunTest(unittest.TestCase):
    def setUp(self):
        self.sampleFile = 'test/sampleFile.txt'
        self.outputFile = 'test/sampleFile.txt.sci'
        self.errFile = 'test/sampleFile.txt.err'


        self.mfe_results = {
            './ps/M35570.1_5-120_dp.pp' : -47.30,
            './ps/X12624.1_61-178_dp.pp': -34.70,
            './ps/M19950.1_1-120_dp.pp' : -34.30,
            './ps/X52300.1_5-122_dp.pp' : -46.00,
            './ps/X54477.1_2-120_dp.pp' : -37.00,
            './ps/X02731.1_3-119_dp.pp' : -38.20
        }

        self.aln_results = {
            './ps/M35570.1_5-120_dp.pp./ps/X12624.1_61-178_dp.pp' : -18.75,
            './ps/M19950.1_1-120_dp.pp./ps/X52300.1_5-122_dp.pp' : -29.90,
            './ps/X54477.1_2-120_dp.pp./ps/X02731.1_3-119_dp.pp' : -20.30
        }

    def test_read_and_run(self):
        read_and_run(self.sampleFile)
        self.assertTrue(os.path.exists(self.outputFile))

    def test_check_content(self):
        self.test_read_and_run()
        ## check that there is 8 field for each line
        with open(self.outputFile) as f:
            next(f)
            for line in f:
                line = line.strip()
                fields = line.split('\t')

                aln_name = "%s%s" % (fields[0], fields[1])

                self.assertEqual(len(fields), 8)
                self.assertEqual(self.mfe_results[fields[0]], float(fields[2]))
                self.assertEqual(self.mfe_results[fields[1]], float(fields[3]))
                self.assertEqual(self.aln_results[aln_name], float(fields[4]))

    def tearDown(self):
        os.unlink(self.outputFile)
        os.unlink(self.errFile)






















