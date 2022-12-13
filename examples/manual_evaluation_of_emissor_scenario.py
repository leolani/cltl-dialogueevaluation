from cltl.dialogue_evaluation.manual_evaluation import ManualEvaluator
import os

evaluator = ManualEvaluator()

emissor_path='/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction1'

for path in os.listdir(emissor_path):
    if os.path.isdir(os.path.join(emissor_path, path)):
        evaluator.evaluate_conversation(emissor_path, path)

