from pathlib import Path

from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator

SCENARIO_FOLDER = './data/3cf7c0b8-f69d-45e8-b804-cb6aca3a044d/'
RDF_FOLDER = SCENARIO_FOLDER + f'rdf/'

#SCENARIO_FOLDER='./data/emissor'
#RDF_FOLDER ='d0fc872d-8199-46a2-94e1-aa739bc9ed7c/'

evaluator = GraphEvaluator()

evaluator.evaluate_conversation(Path(SCENARIO_FOLDER), Path(RDF_FOLDER),
                                metrics_to_plot=['GROUP A - Average degree', 'GROUP A - Sparseness'])
