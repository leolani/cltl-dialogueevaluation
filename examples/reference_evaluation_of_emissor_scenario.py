from cltl.dialogue_evaluation.reference_evaluation import ReferenceEvaluator
import os
from pathlib import Path


evaluator = ReferenceEvaluator()
METRICS = "BLUE"

REFERENCE_SCENARIO = Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction2")
SYSTEM_SCENARIO =  Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction2")
SYSTEM_ID = "0b6a48b4-3afc-44c3-923f-c9dc594314f6"
REFERENCE_ID =  "0b6a48b4-3afc-44c3-923f-c9dc594314f6"

evaluator.evaluate_conversation(ref_scenario_folder=REFERENCE_SCENARIO,
                                sys_scenario_folder=SYSTEM_SCENARIO,
                                ref_scenario_id=REFERENCE_ID,
                                sys_scenario_id=SYSTEM_ID,
                                metrics_to_plot=[METRICS])

