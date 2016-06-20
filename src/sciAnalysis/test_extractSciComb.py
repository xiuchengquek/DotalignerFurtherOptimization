import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from extractSciComb import sciEntry, read_and_find, tdd_read_and_find



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
        print(fh3.write.mock_calls)
        fh3.write.assert_has_calls(calls_list, any_order=False)























if __name__ == '__main__':
    unittest.main()
