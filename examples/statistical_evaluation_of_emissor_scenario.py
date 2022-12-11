from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os

evaluator = StatisticalEvaluator()

emissor_path = '/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction2'
# emissor_path='/Users/piek/Desktop/d-Leolani/docker-configs/robot/storage/emissor'

# for path in os.listdir(emissor_path):
#       print(path)
#       if os.path.isdir(os.path.join(emissor_path, path)):
#           evaluator.analyse_interaction(emissor_path, path)

stats_dict, columns = evaluator.get_overview_statistics(emissor_path)
evaluator.save_overview_statistics(emissor_path, stats_dict, columns)
