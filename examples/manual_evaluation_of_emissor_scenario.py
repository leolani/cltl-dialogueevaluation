from cltl.dialogue_evaluation.manual_evaluation import ManualEvaluator
import os

evaluator = ManualEvaluator()

emissor_path='/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction1'

# for path in os.listdir(emissor_path):
#     if os.path.isdir(os.path.join(emissor_path, path)):
#         evaluator.evaluate_conversation(emissor_path, path)


## To get an oerview of the manual evalations of different scenarios
stats_dict, columns = evaluator.get_manual_evaluation_overview(emissor_path)
evaluator.save_manual_evaluations(emissor_path, stats_dict, columns)