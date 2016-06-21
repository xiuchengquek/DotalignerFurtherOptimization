import unittest
from unittest.mock import patch
from rankAnalysis import  combinationRankBySequence, combinationRankManger, main_run



class combinationRankBySequenceTest(unittest.TestCase):

    def setUp(self):
        combination_rank=  combinationRankBySequence('1')
        combination_rank.add_score('1' , -3)
        combination_rank.add_score('2' , -2)
        combination_rank.add_score('3' , -4)
        combination_rank.add_score('4' , -3)
        self.combination_rank  = combination_rank

    def test_add_score(self):
        combination_rank = self.combination_rank
        self.assertEqual(combination_rank.sequence_pair_id, '1' )
        self.assertListEqual(
            combination_rank.combination_score_dict[-3]['combinations'],
            ['1','4']
        )

        self.assertListEqual(
            combination_rank.combination_score_dict[-2]['combinations'],
            ['2']
        )

        self.assertListEqual(
            combination_rank.combination_score_dict[-4]['combinations'],
            ['3']
        )

    def test_rank_combination(self):
        combination_rank = self.combination_rank
        combination_rank.rank_combination()
        self.assertEqual(
            combination_rank.combination_score_dict[-3]['rank'],
            2
        )

        self.assertEqual(
            combination_rank.combination_score_dict[-2]['rank'],
            1
        )

        self.assertEqual(
            combination_rank.combination_score_dict[-4]['rank'],
            3
        )


    def test_group_by_combination(self):
        combination_rank = self.combination_rank
        combination_rank.rank_combination()
        grouped_score = combination_rank.group_by_combinations()
        self.assertDictEqual(
            grouped_score,
            {
                '1' : 2,
                '2' : 1,
                '3' : 3,
                '4' : 2
            }
        )

class TestCombinationRankManager(unittest.TestCase):
    def setUp(self):
        self.combination_manager = combinationRankManger(combinationRankBySequence)
        child_1 = self.combination_manager.get_or_add_child('1')
        child_1.add_score('1' , -3.0)
        child_1.add_score('2' , -2.0)
        child_1.add_score('3' , -4.0)
        child_1.add_score('4' , -3.0)
        self.child_1 = child_1

        child_2 = self.combination_manager.get_or_add_child('2')

    def test_get_or_add_child(self):
        child_1_same = self.combination_manager.get_or_add_child('1')
        self.assertEqual(self.child_1, child_1_same)
        child_2 = self.combination_manager.get_or_add_child('2')
        self.assertNotEqual(self.child_1, child_2)


    def test_do_combination(self):
        self.combination_manager.sum_up_combination()
        child_1 = self.combination_manager.get_or_add_child('1')
        self.assertEqual(child_1.sequence_pair_id, '1' )
        self.assertListEqual(
            child_1.combination_score_dict[-3]['combinations'],
            ['1','4']
        )

        self.assertListEqual(
            child_1.combination_score_dict[-2]['combinations'],
            ['2']
        )

        self.assertListEqual(
            child_1.combination_score_dict[-4]['combinations'],
            ['3']
        )

    def test_group_by_combination(self):

        child_2 = self.combination_manager.get_or_add_child('2')

        child_2.add_score('1' , -3)
        child_2.add_score('2' , -2)
        child_2.add_score('3' , -42)
        child_2.add_score('4' , -3)

        self.combination_manager.sum_up_combination()
        grouped_score = self.combination_manager.group_by_combination()

        self.assertDictEqual(
            grouped_score,
            {
                '1' : 4,
                '2' : 2,
                '3' : 6,
                '4' : 4
            }
        )

class TestMainRun(unittest.TestCase):

    def setUp(self):

        self.content =[
            'combination\tsequence\tsci-diff',
            '1\t1\t-0.5',
            '2\t1\t-0.2',
            '3\t1\t-0.3',
            '1\t2\t-0.30',
            '2\t2\t-0.30',
            '3\t2\t-0.30'
            ]


        self.content = "\n".join(self.content)

    @patch('builtins.open', spec=open)
    def test_main_run(self, mock_open):

        handle1 = unittest.mock.mock_open(read_data = self.content )
        handle1.return_value.__iter__ = lambda self: self
        handle1.return_value.__next__ = lambda self: self.readline()

        handle2 = unittest.mock.mock_open()
        mock_open.side_effect = (handle1.return_value, handle2.return_value)

        results = main_run('test.in', 'test.out')
        call = unittest.mock.call

        fh_calls = [
            call('test.in'),
            call('test.out', 'w')
        ]

        mock_open.assert_has_calls(fh_calls, any_order=True)
        print(results.children)

        fh_out = handle2()

        fh_out_calls = [
            call('combination\tscore\n'),
            call('1\t4\n'),
            call('2\t2\n'),
            call('3\t3\n')
        ]


        fh_out.write.assert_has_calls(
            fh_out_calls
        )































































if __name__ == '__main__':
    unittest.main()
