from cltl.dialogue_evaluation.manual_evaluation import ManualEvaluator
import os

evaluator = ManualEvaluator()

emissor_path='/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction1'

## To get an overview of the manual evalations of different scenarios
stats_dict, columns = evaluator.get_manual_evaluation_overview(emissor_path)
evaluator.save_manual_evaluations(emissor_path, stats_dict, columns)