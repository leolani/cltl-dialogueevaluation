from pathlib import Path

import pandas as pd
from rdflib import ConjunctiveGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from cltl.dialogue_evaluation.api import BasicEvaluator
from cltl.dialogue_evaluation.metrics.brain_measures import *
from cltl.dialogue_evaluation.metrics.graph_measures import *
from cltl.dialogue_evaluation.metrics.ontology_measures import *
from cltl.dialogue_evaluation.utils.map_rdf_files import map_emissor_scenarios


class GraphEvaluator(BasicEvaluator):
    def __init__(self):
        """Creates an evaluator that will use graph metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        super(GraphEvaluator, self).__init__()
        self._log.debug(f"Graph Evaluator ready")

    def evaluate_conversation(self, scenario_folder, rdf_folder):
        # Read mapping of rdf log file to turn
        map_emissor_scenarios(scenario_folder, rdf_folder)
        full_df = pd.read_json(scenario_folder / f'turn_to_trig_file.json')

        # Recreate conversation and score graph
        rdf_count = 0
        total_turns = len(full_df)
        for idx, row in full_df.iterrows():
            print(f"Processing turn {row['Turn']}/{total_turns}")

            # If first row and no graph
            if idx == 0 and not row['rdf_file']:
                # Calculate metrics on empty graph
                brain_as_graph = ConjunctiveGraph()
                brain_as_netx = rdflib_to_networkx_multidigraph(brain_as_graph)
                full_df = self._calculate_metrics(brain_as_graph, brain_as_netx, full_df, idx)

            # if row has a file to rdf, process it and calculate metrics
            elif row['rdf_file']:
                for file in row['rdf_file']:
                    # Update count
                    rdf_count += 1
                    print(f"\tFound RDF, cumulative: {rdf_count}")

                    # clear brain (for computational purposes)
                    print(f"\tClear brain")
                    brain_as_graph = ConjunctiveGraph()

                    # Add new
                    print(f"\tAdding triples to brains")
                    brain_as_graph.parse(rdf_folder / file, format='trig')
                    brain_as_netx = rdflib_to_networkx_multidigraph(brain_as_graph)

                    # Calculate metrics (only when needed! otherwise copy row)
                    full_df = self._calculate_metrics(brain_as_graph, brain_as_netx, full_df, idx)

            # copy over values from last row to avoid recomputing on an unchanged graph
            else:
                full_df = self._copy_metrics(full_df, idx)

        # Save
        evaluation_folder = Path(scenario_folder / 'evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(full_df, evaluation_folder)

    @staticmethod
    def _calculate_metrics(brain_as_graph, brain_as_netx, df, idx):
        print(f"\tCalculating graph metrics")
        df.loc[idx, 'GROUP A - Total nodes'] = get_count_nodes(brain_as_netx)
        df.loc[idx, 'GROUP A - Total edges'] = get_count_edges(brain_as_netx)
        df.loc[idx, 'GROUP A - Average degree'] = get_avg_degree(brain_as_netx)
        df.loc[idx, 'GROUP A - Average degree centrality'] = get_avg_degree_centr(brain_as_netx)
        df.loc[idx, 'GROUP A - Average closeness'] = get_avg_closeness(brain_as_netx)
        # df.loc[idx, 'GROUP A - Average betweenness'] = get_avg_betweenness(brain_as_netx)
        df.loc[idx, 'GROUP A - Average degree connectivity'] = get_degree_connectivity(brain_as_netx)
        df.loc[idx, 'GROUP A - Average assortativity'] = get_assortativity(brain_as_netx)  # good
        df.loc[idx, 'GROUP A - Average node connectivity'] = get_node_connectivity(brain_as_netx) \
            if get_count_nodes(brain_as_netx) > 0 else 0
        df.loc[idx, 'GROUP A - Number of components'] = get_number_components(brain_as_netx)
        df.loc[idx, 'GROUP A - Number of strong components'] = get_assortativity(brain_as_netx)
        df.loc[idx, 'GROUP A - Shortest path'] = get_shortest_path(brain_as_netx) \
            if get_count_nodes(brain_as_netx) > 0 else 0
        df.loc[idx, 'GROUP A - Centrality entropy'] = get_entropy_centr(brain_as_netx)
        df.loc[idx, 'GROUP A - Closeness entropy'] = get_entropy_clos(brain_as_netx)
        df.loc[idx, 'GROUP A - Sparseness'] = get_sparseness(brain_as_netx) if get_count_nodes(brain_as_netx) > 0 else 0
        ####
        print(f"\tCalculating RDF graph metrics")
        df.loc[idx, 'GROUP B - Total classes'] = get_number_classes(brain_as_graph)
        df.loc[idx, 'GROUP B - Total properties'] = get_number_properties(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total instances']  = get_number_instances(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total object properties']  = get_number_properties_object(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total data properties']  = get_number_properties_datatype(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total equivalent class properties']  = get_number_properties_equivClass(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total subclass properties']  = get_number_properties_subclass(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total entities']  = get_number_entities(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total inverse entities']  = get_number_inverse(brain_as_graph)
        # df.loc[idx, 'GROUP B - Ratio of inverse relations']  = get_ratio_inverse_relations(brain_as_graph)
        # df.loc[idx, 'GROUP B - Property class ratio']  = get_property_class_ratio(brain_as_graph)
        df.loc[idx, 'GROUP B - Average population'] = get_avg_population(brain_as_graph)
        # df.loc[idx, 'GROUP B - Class property ratio']  = get_class_property_ratio(brain_as_graph)
        df.loc[idx, 'GROUP B - Attribute richness'] = get_attribute_richness(brain_as_graph)
        # df.loc[idx, 'GROUP B - Inheritance richness']  = get_inheritance_richness(brain_as_graph)
        df.loc[idx, 'GROUP B - Relationship richness'] = get_relationship_richness(brain_as_graph)
        # df.loc[idx, 'GROUP B - Object properties ratio']  = get_ratio_object_properties(brain_as_graph)
        # df.loc[idx, 'GROUP B - Datatype properties ratio']  = get_ratio_datatype_properties(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total concept assertions']  = get_number_concept_assertions(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total role assertions']  = get_number_role_assertions(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total general concept inclusions']  = get_number_GCI(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total domain axioms']  = get_number_domain_axioms(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total range axioms']  = get_number_range_axioms(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total role inclusions']  = get_number_role_inclusion(brain_as_graph)
        df.loc[idx, 'GROUP B - Total axioms'] = get_number_axioms(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total aBox axioms']  = get_number_aBox_axioms(brain_as_graph)
        # df.loc[idx, 'GROUP B - Total tBox axioms']  = get_number_tBox_axioms(brain_as_graph)
        #####
        print(f"\tCalculating brain metrics")
        df.loc[idx, 'GROUP C - Total triples'] = get_number_triples(brain_as_graph)  # good
        df.loc[idx, 'GROUP C - Total world instances'] = get_number_grasp_instances(brain_as_graph)
        df.loc[idx, 'GROUP C - Total claims'] = get_number_statements(brain_as_graph)
        df.loc[idx, 'GROUP C - Total perspectives'] = get_number_perspectives(brain_as_graph)
        df.loc[idx, 'GROUP C - Total mentions'] = get_number_mentions(brain_as_graph)
        df.loc[idx, 'GROUP C - Total conflicts'] = get_number_negation_conflicts(brain_as_graph)
        df.loc[idx, 'GROUP C - Total sources'] = get_number_sources(brain_as_graph)
        df.loc[idx, 'GROUP C - Total interactions'] = get_number_chats(brain_as_graph)
        df.loc[idx, 'GROUP C - Total utterances'] = get_number_utterances(brain_as_graph)

        df.loc[idx, 'GROUP C - Ratio claim to triples'] = df.loc[idx, 'GROUP C - Total claims'] / df.loc[
            idx, 'GROUP C - Total triples']  # how much knowledge
        df.loc[idx, 'GROUP C - Ratio perspectives to triples'] = df.loc[idx, 'GROUP C - Total perspectives'] / df.loc[
            idx, 'GROUP C - Total triples']  # how much diversity of opinion
        df.loc[idx, 'GROUP C - Ratio conflicts to triples'] = df.loc[idx, 'GROUP C - Total conflicts'] / df.loc[
            idx, 'GROUP C - Total triples']  # how much conflicting info
        df.loc[idx, 'GROUP C - Ratio perspectives to claims'] = df.loc[idx, 'GROUP C - Total perspectives'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of opinions
        df.loc[idx, 'GROUP C - Ratio mentions to claims'] = df.loc[idx, 'GROUP C - Total mentions'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of mentions
        df.loc[idx, 'GROUP C - Ratio conflicts to claims'] = df.loc[idx, 'GROUP C - Total conflicts'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of conflicts

        df.loc[idx, 'GROUP C - Average perspectives per claim'] = get_average_views_per_factoid(brain_as_graph)
        df.loc[idx, 'GROUP C - Average mentions per claim'] = get_average_mentions_per_factoid(brain_as_graph)
        df.loc[idx, 'GROUP C - Average turns per interaction'] = get_average_turns_per_interaction(brain_as_graph)
        df.loc[idx, 'GROUP C - Average claims per source'] = get_average_factoids_per_source(brain_as_graph)
        df.loc[idx, 'GROUP C - Average perspectives per source'] = get_average_views_per_source(brain_as_graph)
        return df

    @staticmethod
    def _copy_metrics(df, idx):
        existing_columns = df.columns
        group_a = ['GROUP A - Total nodes', 'GROUP A - Total edges', 'GROUP A - Average degree',
                   'GROUP A - Average degree centrality', 'GROUP A - Average closeness',
                   'GROUP A - Average betweenness',
                   'GROUP A - Average degree connectivity', 'GROUP A - Average assortativity',
                   'GROUP A - Average node connectivity', 'GROUP A - Number of components',
                   'GROUP A - Number of strong components', 'GROUP A - Shortest path', 'GROUP A - Centrality entropy',
                   'GROUP A - Closeness entropy', 'GROUP A - Sparseness']

        group_b = ['GROUP B - Total classes', 'GROUP B - Total properties', 'GROUP B - Total instances',
                   'GROUP B - Total object properties', 'GROUP B - Total data properties',
                   'GROUP B - Total equivalent class properties', 'GROUP B - Total subclass properties',
                   'GROUP B - Total inverse entities', 'GROUP B - Ratio of inverse relations',
                   'GROUP B - Property class ratio', 'GROUP B - Average population', 'GROUP B - Class property ratio',
                   'GROUP B - Attribute richness', 'GROUP B - Inheritance richness', 'GROUP B - Relationship richness',
                   'GROUP B - Object properties ratio', 'GROUP B - Datatype properties ratio',
                   'GROUP B - Total role assertions', 'GROUP B - Total general concept inclusions',
                   'GROUP B - Total domain axioms', 'GROUP B - Total range axioms', 'GROUP B - Total role inclusions',
                   'GROUP B - Total axioms', 'GROUP B - Total aBox axioms', 'GROUP B - Total tBox axioms'
                   ]

        group_c = ['GROUP C - Total triples', 'GROUP C - Total world instances', 'GROUP C - Total claims',
                   'GROUP C - Total perspectives', 'GROUP C - Total mentions', 'GROUP C - Total conflicts',
                   'GROUP C - Total sources', 'GROUP C - Total interactions', 'GROUP C - Total utterances',
                   'GROUP C - Ratio claim to triples', 'GROUP C - Ratio perspectives to triples',
                   'GROUP C - Ratio conflicts to triples', 'GROUP C - Ratio perspectives to claims',
                   'GROUP C - Ratio mentions to claims', 'GROUP C - Ratio conflicts to claims',
                   'GROUP C - Average perspectives per claim', 'GROUP C - Average mentions per claim',
                   'GROUP C - Average turns per interaction', 'GROUP C - Average claims per source',
                   'GROUP C - Average perspectives per source'
                   ]

        print(f"\tCopying graph metrics")
        for metric in group_a + group_b + group_c:
            if metric in existing_columns:
                df.loc[idx, metric] = df.loc[idx - 1, metric]

        return df

    @staticmethod
    def _save(df, evaluation_folder):

        df = df.drop(columns=['Speaker', 'Response', 'rdf_file'])
        df.to_csv(evaluation_folder / 'graph_evaluation.csv', index=False)
