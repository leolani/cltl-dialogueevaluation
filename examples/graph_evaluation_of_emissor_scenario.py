from cltl.dialogue_evaluation.graph_evaluation import GraphEvaluator

SCENARIO_FOLDER = './data/blender_leolani/2022-05-03-14_35_35/'
RDF_FOLDER = SCENARIO_FOLDER + f'rdf/2022-05-03-14-35/'

#SCENARIO_FOLDER='./data/emissor'
#RDF_FOLDER ='d0fc872d-8199-46a2-94e1-aa739bc9ed7c/'

evaluator = GraphEvaluator()

evaluator.evaluate_conversation(SCENARIO_FOLDER, RDF_FOLDER,
                                metrics_to_plot=['GROUP A - Average degree', 'GROUP A - Sparsity'])
