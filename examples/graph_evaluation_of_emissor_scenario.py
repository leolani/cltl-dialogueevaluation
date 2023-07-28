from pathlib import Path

from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator

SCENARIOS_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction2")
SCENARIOS = sorted([path for path in SCENARIOS_FOLDER.iterdir()
                    if path.is_dir() and path.stem not in ['.idea', 'plots']])

evaluator = GraphEvaluator()

for SCENARIO_FOLDER in SCENARIOS:
    evaluator.evaluate_conversation(SCENARIO_FOLDER, rdf_folder=Path(SCENARIO_FOLDER / f'rdf/'))
