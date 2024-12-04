from cltl.dialogue_evaluation.manual_evaluation import ManualEvaluator
import os

evaluator = ManualEvaluator()

submissions_path = '/Users/piek/Desktop/t-MA-Combots-2023/assignments/interactions/submissions-1'

for path in os.listdir(submissions_path):
    student_path = os.path.join(submissions_path, path)
    if os.path.isdir(student_path):




emissor_path = '/Users/piek/Desktop/t-MA-Combots-2023/assignments/interactions/submissions-1'

## To get an overview of the manual evalations of different scenarios
stats_dict, columns = evaluator.get_manual_evaluation_overview(emissor_path)
evaluator.save_manual_evaluations(emissor_path, stats_dict, columns)