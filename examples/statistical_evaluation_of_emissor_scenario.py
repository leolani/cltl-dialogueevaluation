from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os
evaluator = StatisticalEvaluator()

emissor_path='/Users/piek/Desktop/t-MA-Combots-2023/assignments/interactions/submissions-1/angus-mark'
#emissor_path='/Users/piek/Desktop/d-Leolani/docker-configs/robot/storage/emissor'
scenario = "5d89bd79-5c18-407c-b5f5-2f2c4adfe362"

evaluator.analyse_interaction(emissor_path, scenario)

stats_dict, columns = evaluator.get_overview_statistics(emissor_path)
evaluator.save_overview_statistics(emissor_path, stats_dict, columns)
