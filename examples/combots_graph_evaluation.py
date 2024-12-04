from pathlib import Path

from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator
from cltl.dialogue_evaluation.metrics_plotting import Plotter

SCENARIOS_FOLDER = Path("/Users/sbaez/Downloads/interactions-1/all_valid")
SCENARIOS = sorted([path for path in SCENARIOS_FOLDER.iterdir() if path.is_dir() and path.stem != '.idea'])

graph_evaluator = GraphEvaluator()
for SCENARIO_FOLDER in SCENARIOS:
    graph_evaluator.evaluate_conversation(SCENARIO_FOLDER, rdf_folder=Path(SCENARIO_FOLDER / f'rdf/'))

plotter = Plotter()
plotter.plot_conversations(SCENARIOS_FOLDER,
                           metrics=['GROUP A - Average degree', 'GROUP A - Sparseness', #'GROUP A - Shortest path',
                                    'GROUP A - Number of components', 'GROUP A - Centrality entropy',
                                    'GROUP B - Average population',
                                    'GROUP C - Total triples', 'GROUP C - Total world instances',
                                    'GROUP C - Total claims',
                                    'GROUP C - Total perspectives', 'GROUP C - Total mentions',
                                    'GROUP C - Total conflicts',
                                    'GROUP C - Total sources', 'GROUP C - Total interactions',
                                    'GROUP C - Total utterances',
                                    'GROUP C - Ratio claim to triples', 'GROUP C - Ratio perspectives to triples',
                                    'GROUP C - Ratio conflicts to triples', 'GROUP C - Ratio perspectives to claims',
                                    'GROUP C - Ratio mentions to claims', 'GROUP C - Ratio conflicts to claims',
                                    'GROUP C - Average perspectives per claim', 'GROUP C - Average mentions per claim',
                                    'GROUP C - Average turns per interaction', 'GROUP C - Average claims per source',
                                    'GROUP C - Average perspectives per source'])
