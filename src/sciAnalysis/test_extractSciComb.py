import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from extractSciComb import sciEntry, read_and_find
from SciDiffAnalysis import SciDiffAnalysis
from collections import OrderedDict



class testSciEntry(unittest.TestCase):
    def test_init(self):
        sciA = sciEntry('seqA', 'seqB', 0.1)
        self.assertEqual(sciA.sequence_a, 'seqA')
        self.assertEqual(sciA.sequence_b, 'seqB')
        self.assertEqual(sciA.sci, 0.1)
        self.assertEqual(sciA.id, 'seqA seqB')
        self.assertEqual(sciA.is_diff, False)

        sciB = sciEntry('seqC', 'seqD', 0.1, is_diff=True)
        self.assertEqual(sciB.sequence_a, 'seqC')
        self.assertEqual(sciB.sequence_b, 'seqD')
        self.assertEqual(sciB.sci, 0.1)
        self.assertEqual(sciB.id, 'seqC seqD')
        self.assertEqual(sciB.is_diff, True)

    def test_from_string(self):
        sci_string = 'seqA\tseqB\tseqC\t\tasdas\tssd\t0.1'
        sciA = sciEntry.from_string(sci_string)
        sciA = sciEntry('seqA', 'seqB', 0.1)
        self.assertEqual(sciA.sequence_a, 'seqA')
        self.assertEqual(sciA.sequence_b, 'seqB')
        self.assertEqual(sciA.sci, 0.1)
        self.assertEqual(sciA.id, 'seqA seqB')
        self.assertEqual(sciA.is_diff, False)


    def test_from_reference(self):
        reference_content = [ "index,SequenceA,SequenceB,SCI",
                              "0,AF254716.1_405-461,AF457085.1_8773-8829,0.9",
                              "1,AF443080.1_1454-1505,AY322185.1_1538-1589,1.0",
                              ]

        m = unittest.mock.mock_open(read_data='\n'.join(reference_content))
        m.return_value.__iter__ = lambda self: self
        m.return_value.__next__ = lambda self: self.readline()


        with mock.patch('builtins.open',m ):
            reference_entries = sciEntry.from_reference(reference_content)
            ids =  [x.id for x in reference_entries ]
            scis = [x.sci for x in reference_entries ]
            sequenceAs = [x.sequence_a for x in reference_entries]
            sequenceBs = [x.sequence_b for x in reference_entries]
            self.assertListEqual(['AF254716.1_405-461 AF457085.1_8773-8829' ,
                                  'AF443080.1_1454-1505 AY322185.1_1538-1589'],
                                 ids
                                 )
            self.assertListEqual([0.9,1.0] , scis, )
            self.assertListEqual(['AF254716.1_405-461', 'AF443080.1_1454-1505'], sequenceAs)
            self.assertListEqual(['AF457085.1_8773-8829', 'AY322185.1_1538-1589'], sequenceBs)

    def test_operator(self):
        sciA =  sciEntry('seqA', 'seqB', 0.1)
        refSciA = sciEntry('seqA', 'seqB', 0.2)
        sciC = sciA - refSciA
        self.assertEqual(sciC.is_diff, True)
        self.assertEqual(sciC.sequence_a, 'seqA')
        self.assertEqual(sciC.sequence_b, 'seqB')
        self.assertEqual(sciC.sci, -0.1)



    def test_exception_thrown(self):
        sciA =  sciEntry('seqA', 'seqB', 0.1)
        refSciA = sciEntry('seqC', 'seqD', 0.2)
        t = lambda x, y : x - y
        self.assertRaises(ValueError, t, refSciA, sciA)


    def test_get_parameters(self):
        filename = 'e-0.05_o-1_t-0.4_k-0.1_T-10_S-50.dotaligner.out.sci'
        parameters = sciEntry.get_parameters(filename)
        self.assertDictEqual({
            'e' : '0.05',
            'o' : '1',
            't' : '0.4',
            'k' : '0.1',
            'T' : '10',
            'S' : '50'
        }, parameters)


    def test_to_string(self):
        sciA =  sciEntry('seqA', 'seqB', 0.1)
        self.assertEqual(sciA.to_string(), 'seqA\tseqB\t0.100000')
        refSciA = sciEntry('seqA', 'seqB', 0.2)
        sciC = sciA - refSciA
        self.assertEqual(sciC.is_diff, True)
        self.assertEqual(sciC.sequence_a, 'seqA')
        self.assertEqual(sciC.sequence_b, 'seqB')
        self.assertEqual(sciC.sci, -0.1)

    def test_clean_sequence_name(self):
        sequence_name = 'data/ps/seqA_dp.pp'
        clean_sequence_name= sciEntry.clean_sequence_name(sequence_name)
        self.assertEqual('seqA' , clean_sequence_name)



class testReadAndFind(unittest.TestCase):
    def setUp(self):
        self.reference_content = [ "index,SequenceA,SequenceB,SCI",
                              "0,seqA,seqB,0.9",
                              "1,seqC,seqD,1.0"
                              ]

        self.sci_file_content = [
            "SequenceA\tSequenceB\tSequenceA_MFE\tSequenceB_MFE\tAln_MFEtAln_MFE_Raw\tAln_MFE_offset\tSCI",
            "data/ps/seqA_dp.pp\tdata/ps/seqB_dp.pp\t-47.3\t-34.7\t-26.9\t-27.9\t1.0\t0.1"
        ]

        self.reference_file_name = 'reference.csv'
        self.sci_file_name = 'e-0.05_o-1_t-0.4_k-0.1_T-10_S-50.dotaligner.out.sci'
        self.outname ='e-0.05_o-1_t-0.4_k-0.1_T-10_S-50.dotaligner.out.sci.diff'



    @patch('builtins.open', spec=open)
    def test_read_and_find(self, mock_open):
        handle1 = unittest.mock.mock_open(read_data="\n".join(self.reference_content))
        handle1.return_value.__iter__ = lambda self: self
        handle1.return_value.__next__ = lambda self: self.readline()



        handle2 = unittest.mock.mock_open(read_data="\n".join(self.sci_file_content))
        handle2.return_value.__iter__ = lambda self: self
        handle2.return_value.__next__ = lambda self: self.readline()

        handle3 = unittest.mock.mock_open()

        mock_open.side_effect = (handle1.return_value, handle2.return_value, handle3.return_value)

        read_and_find(self.reference_file_name, self.sci_file_name)
        calls = unittest.mock.call
        calls_list = [
            calls('e\to\tt\tk\tT\tS\tSequenceA\tSequenceB\tsci-diff\n'),
            calls('0.05\t1\t0.4\t0.1\t10\t50\tseqA\tseqB\t-0.800000\n')
        ]
        fh3 = handle3()
        fh3.write.assert_has_calls(calls_list, any_order=False)

class SciDiffAnalysisTest(unittest.TestCase):

    def setUp(self):
        self.example_row = OrderedDict(
            [('e' , '0.05'),
            ('o', '1'),
            ('t',  '0.4'),
            ('k', '0.1'),
            ('T', '10'),
            ('S', '1'),
            ('SequenceA', 'SeqA'),
            ('SequenceB', 'SeqB'),
            ('sci-diff', '-1')]
        )
        self.parameters = ['e','o','t','k','T','S']
        self.files = ['file.sci', 'file.sci.diff', 'file2.sci.diff']





    def test_init(self):
        m_list = MagicMock(return_value = self.files)
        with mock.patch('os.listdir',  m_list) as m :
            sci_diff_analysis = SciDiffAnalysis('mockdir', self.parameters)
            self.assertListEqual(sci_diff_analysis.files, [ 'mockdir/file.sci.diff', 'mockdir/file2.sci.diff'])
            self.assertListEqual(sci_diff_analysis.parameters, ['e','o','t','k','T','S'])
            self.assertEqual(sci_diff_analysis.combinations, {})
            self.assertEqual(sci_diff_analysis.sequence_pair, {})
            self.assertEqual(sci_diff_analysis.combination_counter, 0)
            self.assertEqual(sci_diff_analysis.sequence_counter, 0)

    def test_get_combination(self):
        m_list = MagicMock(return_value = self.files)
        with mock.patch('os.listdir',  m_list) as m :
            sci_diff_analysis = SciDiffAnalysis('mockdir', self.parameters)
            combination = sci_diff_analysis.get_combination(self.example_row)
            self.assertEqual(combination, '0.05\t1\t0.4\t0.1\t10\t1')

            entry_index = sci_diff_analysis.add_to_combination(combination)
            self.assertEqual(entry_index, 1)

            entry_index = sci_diff_analysis.add_to_combination(combination)
            self.assertEqual(entry_index,1)

            combination_2 = '0.10\t2\t0.1\t1\t1'
            entry_index = sci_diff_analysis.add_to_combination(combination_2)
            self.assertEqual(entry_index, 2)



        fh_out = unittest.mock.mock_open(read_data = "\n".join(['index\te\to\tt\tk\tT\tS', '1\t0.05\t1\t0.4\t0.1\t10\t1', '2\t0.10\t2\t0.1\t1\t1']))
        call = unittest.mock.call

        with mock.patch('builtins.open', fh_out) as m:
            sci_diff_analysis.write_combination('combination.index.txt')
            fo = m()
            fo.write.assert_has_calls(
                [call('index\te\to\tt\tk\tT\tS\n'),
                 call('1\t0.05\t1\t0.4\t0.1\t10\t1\n'),
                 call('2\t0.10\t2\t0.1\t1\t1\n')
                ]
            )



    def test_get_add_write_sequence(self):
        m_list = MagicMock(return_value = self.files)

        with mock.patch('os.listdir',  m_list) as m :
            sci_diff_analysis = SciDiffAnalysis('mockdir', self.parameters)

            sequence_name = sci_diff_analysis.get_sequence_pair(self.example_row)
            self.assertEqual(sequence_name, 'SeqA\tSeqB')

            entry_index = sci_diff_analysis.add_to_sequence_pair(sequence_name)
            self.assertEqual(entry_index, 1 )

            entry_index = sci_diff_analysis.add_to_sequence_pair(sequence_name)
            self.assertEqual(entry_index, 1 )

            entry_index = sci_diff_analysis.add_to_sequence_pair('SeqC\tSeqD')
            self.assertEqual(entry_index, 2)

        fh_out = unittest.mock.mock_open(read_data="\n".join(['index\tSequenceA\tSequenceB', '1\tSeqA\tSeqB', '2\tSeqC\tSeqD']))
        call = unittest.mock.call
        with mock.patch('builtins.open', fh_out ) as m:
            sci_diff_analysis.write_sequence('seq.index.txt')
            fo = m()
            fo.write.assert_has_calls(
                [call('index\tSequenceA\tSequenceB\n'),call('1\tSeqA\tSeqB\n'), call('2\tSeqC\tSeqD\n')]
            )







    @patch('builtins.open', spec=open)
    def test_read_and_count(self, mock_open):

        header = 'e\to\tt\tk\tT\tS\tSequenceA\tSequenceB\tsci-diff'
        file1_content = [ header, '0.05\t1\t0.5\t1\t1\t1\tSeqA\tSeqB\t1',  '0.05\t1\t0.5\t1\t1\t1\tSeqB\tSeqC\t1']
        file2_content = [ header, '0.05\t2\t0.5\t2\t1\t1\tSeqA\tSeqB\t1',  '0.05\t2\t0.5\t2\t1\t1\tSeqB\tSeqC\t1']

        handle1 = unittest.mock.mock_open(read_data="\n".join(file1_content))
        handle1.return_value.__iter__ = lambda self: self
        handle1.return_value.__next__ = lambda self: self.readline()

        handle2 = unittest.mock.mock_open(read_data="\n".join(file2_content))
        handle2.return_value.__iter__ = lambda self: self
        handle2.return_value.__next__ = lambda self: self.readline()
        handle3 = unittest.mock.mock_open()

        mock_open.side_effect = (handle3.return_value, handle1.return_value, handle2.return_value)
        m_list = MagicMock(return_value = self.files)
        with mock.patch('os.listdir',  m_list) as m :
            sci_diff_obj = SciDiffAnalysis('mocks', self.parameters)
            sci_diff_obj.read_and_count_write('output.txt')

        call = unittest.mock.call


        file_open_calls = [
            call('output.txt', 'w'),
            call('mocks/file.sci.diff', 'r'),
            call('mocks/file2.sci.diff', 'r')


        ]

        mock_open.assert_has_calls(file_open_calls)

        fh_out = handle3()
        fh_out.write.assert_has_calls(
            [
                call('combination\tsequence\tsci-diff\n'),
                call('1\t1\t1\n'),
                call('1\t2\t1\n'),
                call('2\t1\t1\n'),
                call('2\t2\t1\n')

            ]
        )


if __name__ == '__main__':
    unittest.main()
