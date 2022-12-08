from pathlib import Path
import os
from pathlib import Path
from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator

SCENARIOS_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2022/assignments/interaction2")

evaluator = GraphEvaluator()

for path in os.listdir(SCENARIOS_FOLDER):
    SCENARIO_FOLDER = os.path.join(SCENARIOS_FOLDER, path)

    if os.path.isdir(SCENARIO_FOLDER):
        print(SCENARIO_FOLDER)
        RDF_FOLDER = os.path.join(SCENARIO_FOLDER, 'rdf')
        evaluator.evaluate_conversation(Path(SCENARIO_FOLDER), Path(RDF_FOLDER),
                                        metrics_to_plot=['GROUP A - Average degree', 'GROUP A - Sparseness'])
