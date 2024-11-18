from cltl.dialogue_evaluation.reference_evaluation import ReferenceEvaluator
from pathlib import Path


evaluator = ReferenceEvaluator()
METRIC = ["blue", "rouge", "bertscore", "meteor"]
#nlg_metrics =['rouge','blue','sacrebleu','bleurt', 'meteor','google_bleu', 'harshhpareek/bertscore', 'all']


REFERENCE_SCENARIO = Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction2")
SYSTEM_SCENARIO =  Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction2")
SYSTEM_ID = "4ae67886-0f67-4b66-87c1-eb3b0a2c4426"
REFERENCE_ID =  "4ae67886-0f67-4b66-87c1-eb3b0a2c4426"
path = "/Users/piek/Desktop/t-MA-Combots-2023/combots-lectures-2023/week3/emissor/"

evaluator.evaluate_conversation_two_scenarios(ref_scenario_folder=path,
                                sys_scenario_folder=path,
                                ref_scenario_id=REFERENCE_ID,
                                sys_scenario_id=SYSTEM_ID,
                                metrics_to_plot=METRIC)

# evaluator.evaluate_conversation_two_scenarios(ref_scenario_folder=REFERENCE_SCENARIO,
#                                 sys_scenario_folder=SYSTEM_SCENARIO,
#                                 ref_scenario_id=REFERENCE_ID,
#                                 sys_scenario_id=SYSTEM_ID,
#                                 metrics_to_plot=METRIC)