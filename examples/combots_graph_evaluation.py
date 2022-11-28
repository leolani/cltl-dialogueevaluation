from pathlib import Path

from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator
from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator

SCENARIOS_FOLDER = Path("/Users/sbaez/Downloads/interaction1")
SCENARIOS = sorted([path for path in SCENARIOS_FOLDER.iterdir() if path.is_dir() and path.stem != '.idea'])

for SCENARIO_FOLDER in SCENARIOS:
    evaluator = GraphEvaluator()
    evaluator.evaluate_conversation(Path(SCENARIO_FOLDER), Path(SCENARIO_FOLDER / f'rdf/'),
                                    metrics_to_plot=['GROUP A - Average degree', 'GROUP A - Sparseness'])

    evaluator = LikelihoodEvaluator(model_path_mlm='adamlin/usr-topicalchat-roberta_ft', max_context=300,
                                    len_top_tokens=20)
    evaluator.evaluate_conversation(scenario_folder=SCENARIOS_FOLDER,
                                    scenario_id=SCENARIO_FOLDER.stem,
                                    metrics_to_plot=['MLM llh'])
