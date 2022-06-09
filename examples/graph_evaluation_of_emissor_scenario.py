from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator

SCENARIO_FOLDER = './data/blender_leolani/2022-05-03-14_35_35/'
RDF_FOLDER = SCENARIO_FOLDER + f'rdf/2022-05-03-14-35/'

evaluator = GraphEvaluator()

evaluator.evaluate_conversation(SCENARIO_FOLDER, RDF_FOLDER, metrics_to_plot=['GROUP A - Average degree'])
