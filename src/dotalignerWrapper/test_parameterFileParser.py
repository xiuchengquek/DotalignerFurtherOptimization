import unittest
from unittest import mock
from parameterFileParser import parse_pairwise_alignments, parse_param_file
from dotalignerWrapper import DotAlignerWrapper, DotAlignerGrouped
from collections import OrderedDict




class TestPairListParameters(unittest.TestCase):

    def setUp(self):
        self.file_content = ['M35570.1_5-120\tX12624.1_61-178\tapsi-37\tsci-107\tno-1',
                             'M19950.1_1-120\tX52300.1_5-122\tapsi-37\tsci-89\tno-1']
        self.file_name = "test.txt"

    def test_parse_pairwise_alignments(self):
        m = unittest.mock.mock_open(read_data='\n'.join(self.file_content))
        m.return_value.__iter__ = lambda self: self
        m.return_value.__next__ = lambda self: self.readline()
        with mock.patch('builtins.open',m ):
            results = parse_pairwise_alignments(self.file_name)
        self.assertEqual(results, [['M35570.1_5-120' , 'X12624.1_61-178'], ['M19950.1_1-120', 'X52300.1_5-122']])




class TestParameters(unittest.TestCase):
    def setUp(self):
        self.file_content = ['Parameters\tValue', 'e\t1,2','k\t2']
        self.file_name = "text.txt"


    def test_parse_param_file(self):
        m = unittest.mock.mock_open(read_data='\n'.join(self.file_content))
        m.return_value.__iter__ = lambda self: self
        m.return_value.__next__ = lambda self: self.readline()
        with mock.patch('builtins.open',m ):
            results = parse_param_file(self.file_name)

        self.assertDictEqual(results, {"e" : ['1', '2'] , 'k' : ['2']})


class TestDotAlignerWrapper(unittest.TestCase):

    def side_effect(self, file_name):
        if file_name == '/found':
            return True
        else :
            return False

    def test_dotaligner_wrapper(self):
        mock_object = unittest.mock.Mock( side_effect=self.side_effect)
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerWrapper('/found')
        self.assertIsNotNone(da)
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            self.assertRaises(FileNotFoundError, DotAlignerWrapper, '/unfound')

    def test_dotaligner_wrapper_add_params(self):

        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        params  = {"e" : ['10','20']}
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerWrapper('/found')
            da.update_parameters(params)
            self.assertDictEqual(da.params_dict,    {
            'e' : ['10','20'],
            'o' : ['1'],
            't' : ['0.5'],
            'k' : ['0.5'],
            'T' : ['1'],
            'S' : ['10'],
        })


    def test_get_combinatios(self):
        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        params  = {"e" : ['10','20']}
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerWrapper('/found')
            da.update_parameters(params)
            comb_iter = da.get_combinations()
            comb_iter = list(comb_iter)
        self.assertListEqual(comb_iter,
                             [{'e' : '10', 'o': '1' ,'t' : '0.5' , 'k' : '0.5', 'T' : '1', 'S' : '10' },
                              {'e' : '20', 'o': '1' ,'t' : '0.5' , 'k' : '0.5', 'T' : '1', 'S' : '10' }])

    def test_add_pairs(self):
        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        params  = {"e" : ['10','20']}
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerWrapper('/found')
            da.add_pairs([['a', 'b']])
            self.assertListEqual(da.pairs,[ ['a','b']])

    def test_generate_and_run(self):
        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            with unittest.mock.patch.object(DotAlignerWrapper, 'run_dotaligner') as dot_mock:
                da = DotAlignerWrapper('/found')
                da.add_pairs([['a', 'b']])
                da.generate_and_run()
                dot_mock.assert_called_with(
                    "(time -f '\\t%E\\t%M' /found -k 0.5 -t 0.5 -o 1 -e 0.2 -s 10 -T 1 -d a_dp.pp -d b_dp.pp; ) >> out/k_0.5-t_0.5-o_1-e_0.2-T_1.dotaligner.out 2>&1",
                    ['a','b'],
                    OrderedDict([('e', '0.2'), ('o', '1'), ('t', '0.5'), ('k', '0.5'), ('T', '1'), ('S', '10')])
                )

class TestDotAlignerGrouped(unittest.TestCase):
    def side_effect(self, file_name):
        if file_name == '/found':
            return True
        else :
            return False

    def test_initialization(self):
        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerGrouped('/found')
            self.assertEqual(da.current_id, None)
            self.assertEqual(da.command_list, [])

    def test_run_dotaligner(self):
        fh = unittest.mock.mock_open()
        mock_object = unittest.mock.Mock( side_effect= self.side_effect)
        with unittest.mock.patch('os.path.exists', mock_object ) as m :
            da = DotAlignerGrouped('/found')
            da.add_pairs([['a','b'], ['b','c']])
            params  = {"e" : ['10','20']}
            da.update_parameters(params)
            with unittest.mock.patch('builtins.open', fh):
                da.generate_and_run()
                calls = unittest.mock.call
                calls_list = [calls('e_10_o_1_t_0.5_k_0.5_T_1_S_10' ,'w'), calls('e_20_o_1_t_0.5_k_0.5_T_1_S_10' ,'w')]
                fh.assert_has_calls(calls_list, any_order=True)
                handle = fh()
                calls_list =  [
                    calls("(time -f '\\t%E\\t%M' /found -k 0.5 -t 0.5 -o 1 -e 10 -s 10 -T 1 -d a_dp.pp -d b_dp.pp; ) >> out/k_0.5-t_0.5-o_1-e_10-T_1.dotaligner.out 2>&1\n" +\
                          "(time -f '\\t%E\\t%M' /found -k 0.5 -t 0.5 -o 1 -e 10 -s 10 -T 1 -d b_dp.pp -d c_dp.pp; ) >> out/k_0.5-t_0.5-o_1-e_10-T_1.dotaligner.out 2>&1"),
                    calls("(time -f '\\t%E\\t%M' /found -k 0.5 -t 0.5 -o 1 -e 20 -s 10 -T 1 -d a_dp.pp -d b_dp.pp; ) >> out/k_0.5-t_0.5-o_1-e_20-T_1.dotaligner.out 2>&1\n" +\
                          "(time -f '\\t%E\\t%M' /found -k 0.5 -t 0.5 -o 1 -e 20 -s 10 -T 1 -d b_dp.pp -d c_dp.pp; ) >> out/k_0.5-t_0.5-o_1-e_20-T_1.dotaligner.out 2>&1")
                ]
                handle.write.assert_has_calls(calls_list)

if __name__ == '__main__':
    unittest.main()
