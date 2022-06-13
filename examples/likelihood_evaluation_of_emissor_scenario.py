from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator

evaluator = LikelihoodEvaluator(model_path_mlm='adamlin/usr-topicalchat-roberta_ft', max_context=300,
                                len_top_tokens=20)
evaluator.evaluate_conversation(scenario_folder='./data/blender_leolani/', scenario_id='2022-05-03-14_35_35',
                                metrics_to_plot=['MLM llh'])
