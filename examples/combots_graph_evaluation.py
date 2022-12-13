from pathlib import Path

from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator
from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator
from cltl.dialogue_evaluation.metrics_correlations import Correlator
from cltl.dialogue_evaluation.metrics_plotting import Plotter
from cltl.dialogue_evaluation.utils.constants import GRAPH_METRICS, LIKELIHOOD_METRICS, HUMAN_METRICS

SCENARIOS_FOLDER = Path("/Users/sbaez/Downloads/interaction1")
# SCENARIOS_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction1")
SCENARIOS = sorted([path for path in SCENARIOS_FOLDER.iterdir()
                    if path.is_dir() and path.stem not in ['.idea', 'plots']])

graph_evaluator = GraphEvaluator()
usr_evaluator = LikelihoodEvaluator(model_path_mlm='adamlin/usr-topicalchat-roberta_ft', max_context=300,
                                    len_top_tokens=20)
# for SCENARIO_FOLDER in SCENARIOS:
#     graph_evaluator.evaluate_conversation(SCENARIO_FOLDER, rdf_folder=Path(SCENARIO_FOLDER / f'rdf/'))
#     usr_evaluator.evaluate_conversation(SCENARIOS_FOLDER, scenario_id=SCENARIO_FOLDER.stem)

plotter = Plotter()
plotter.plot_conversations(SCENARIOS_FOLDER,
                           metrics=['GROUP A - Average degree', 'GROUP A - Sparseness', #'GROUP A - Shortest path',
                                    'GROUP A - Number of components', 'GROUP A - Centrality entropy',
                                    'GROUP B - Average population',
                                    'GROUP C - Ratio claim to triples', 'GROUP C - Ratio perspectives to claims',
                                    'MLM llh'])

correlator = Correlator()
correlator.correlate_metrics(SCENARIOS_FOLDER,
                             metrics=GRAPH_METRICS + LIKELIHOOD_METRICS + HUMAN_METRICS)
