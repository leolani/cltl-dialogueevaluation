from pathlib import Path

from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator
from cltl.dialogue_evaluation.usr_dialogue_retrieval_evaluation import USR_DialogRetrieval_Evaluator

SCENARIOS_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction3")
SCENARIOS = sorted([path for path in SCENARIOS_FOLDER.iterdir()
                    if path.is_dir() and path.stem not in ['.idea', 'plots']])

evaluator = LikelihoodEvaluator(model_path_mlm='adamlin/usr-topicalchat-roberta_ft', max_context=300, len_top_tokens=20)

# evaluator = USR_DialogRetrieval_Evaluator(model_path_ctx='adamlin/usr-topicalchat-ctx', context_type="ctx",
#                                           max_context=300, len_top_tokens=20)
#
# evaluator = USR_DialogRetrieval_Evaluator(model_path_ctx='adamlin/usr-topicalchat-uk', context_type="fct",
#                                           max_context=300, len_top_tokens=20)

for SCENARIO_FOLDER in SCENARIOS:
    evaluator.evaluate_conversation(scenario_folder=SCENARIOS_FOLDER, scenario_id=SCENARIO_FOLDER.stem)
