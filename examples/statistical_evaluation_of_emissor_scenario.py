from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os
evaluator = StatisticalEvaluator()

#evaluator.evaluate_conversation('./data/emissor/', 'd0fc872d-8199-46a2-94e1-aa739bc9ed7c')
emissor_path='/Users/piek/Desktop/d-Leolani/docker-configs/chatonly-docker/storage/emissor'

for path in os.listdir(emissor_path):
    if os.path.isdir(os.path.join(emissor_path, path)):
        evaluator.analyse_interaction(emissor_path, path)
