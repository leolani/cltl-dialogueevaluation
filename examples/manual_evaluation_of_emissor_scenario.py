from cltl.dialogue_evaluation.manual_evaluation import ManualEvaluator

evaluator = ManualEvaluator()

emissor_path='/Users/piek/Desktop/d-Leolani/docker-configs/chatonly-docker/storage/emissor'
evaluator.evaluate_conversation(emissor_path, '2fe112e2-31cf-4aef-9011-d237135e53fb')
