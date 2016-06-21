#!/usr/bin/env python


from collections import deque, defaultdict, Counter, OrderedDict
import csv
import argparse


class combinationRankBySequence:

    def __init__(self, sequence_pair_id):
        self.sequence_pair_id = sequence_pair_id
        self.combination_score_dict = defaultdict(dict)

    def add_score(self, combination, score):
        if 'combinations' not in self.combination_score_dict[score]:
            self.combination_score_dict[score] = {
                'combinations' : [],
                'rank' : None
            }
        self.combination_score_dict[score]['combinations'].append(combination)

    def rank_combination(self):
        scores = self.combination_score_dict.keys()
        unique_scores = set(scores)
        unique_scores = list(unique_scores)
        unique_scores.sort(reverse=True)
        for ix, x in enumerate(unique_scores):
            rank = ix + 1
            self.combination_score_dict[x]['rank'] = rank

    def group_by_combinations(self):
        grouped_score = {}
        for score, combinations in self.combination_score_dict.items():
            for x in combinations['combinations']:
                grouped_score[x] = combinations['rank']
        return grouped_score

class combinationRankManger:

    def __init__(self, children_class):
        self.children = OrderedDict({})
        self.children_class = children_class

    def get_or_add_child(self, sequence_pair_id):
        if sequence_pair_id not in self.children:
            self.children[sequence_pair_id] = self.children_class(sequence_pair_id)
        return self.children[sequence_pair_id]

    def sum_up_combination(self):
        for key, value in self.children.items():
            value.rank_combination()

    def group_by_combination(self):
        grouped_score = Counter()
        for sequence_id, children in self.children.items():
            grouped = children.group_by_combinations()
            for keys, value in grouped.items():
                grouped_score[keys] += value
        return grouped_score

def main_run(merged_sci_diff, output):
    rank_manager = combinationRankManger(combinationRankBySequence)
    with open(merged_sci_diff)  as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            sequence = row['sequence']
            child = rank_manager.get_or_add_child(sequence)
            child.add_score(row['combination'], float(row['sci-diff']))

    rank_manager.sum_up_combination()
    grouped_score = rank_manager.group_by_combination()

    with open(output, 'w') as f:
        f.write('combination\tscore\n')
        for keys, value in grouped_score.items():
            f.write("%s\t%s\n" %(keys, value))


    return rank_manager






if __name__ == '__main__':
    parser = argparse.ArgumentParser
    parser.add_argument('-m', '--mergedfile', 'merged sci file')
    parser.add_argument('-o', '--output', 'output file')

    args = parser.parse_args()


    main_run(args.mergedfile, args.output)

















