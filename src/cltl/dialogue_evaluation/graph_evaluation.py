from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
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

    def evaluate_conversation(self, scenario_folder, rdf_folder, metrics_to_plot=None):
        # Read mapping of rdf log file to turn
        map_emissor_scenarios(scenario_folder, rdf_folder)
        full_df = pd.read_json(scenario_folder + f'turn_to_trig_file.json')

        # Recreate conversation and score graph
        rdf_count = 0
        total_turns = len(full_df)
        for idx, row in full_df.iterrows():
            print(f"Processing turn {row['Turn']}/{total_turns}")

            # if row has a file to rdf, process it and calculate metrics
            if row['rdf_file']:
                for file in row['rdf_file']:
                    # Update count
                    rdf_count += 1
                    print(f"\tFound RDF, cumulative: {rdf_count}")

                    # clear brain (for computational purposes)
                    print(f"\tClear brain")
                    brain_as_graph = ConjunctiveGraph()

                    # Add new
                    print(f"\tAdding triples to brains")
                    brain_as_graph.parse(rdf_folder + file, format='trig')
                    brain_as_netx = rdflib_to_networkx_multidigraph(brain_as_graph)

                    # Calculate metrics (only when needed! otherwise copy row)
                    full_df = self._calculate_metrics(brain_as_graph, brain_as_netx, full_df, idx)

            # copy over values from last row to avoid recomputing on an unchanged graph
            else:
                full_df = self._copy_metrics(full_df, idx)

        # Save
        evaluation_folder = Path(scenario_folder + 'evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(full_df, evaluation_folder)

        if metrics_to_plot:
            self.plot_metrics_progression(metrics_to_plot, [full_df], evaluation_folder)

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
        df.loc[idx, 'GROUP A - Average node connectivity'] = get_node_connectivity(brain_as_netx)
        df.loc[idx, 'GROUP A - Number of components'] = get_number_components(brain_as_netx)
        df.loc[idx, 'GROUP A - Number of strong components'] = get_assortativity(brain_as_netx)
        # df.loc[idx, 'GROUP A - Shortest path'] = get_shortest_path(brain_as_netx)
        df.loc[idx, 'GROUP A - Centrality entropy'] = get_entropy_centr(brain_as_netx)
        df.loc[idx, 'GROUP A - Closeness entropy'] = get_entropy_clos(brain_as_netx)
        df.loc[idx, 'GROUP A - Sparseness'] = get_sparseness(brain_as_netx)  # good
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
        print(f"\tCopying graph metrics")
        df.loc[idx, 'GROUP A - Total nodes'] = df.loc[idx - 1, 'GROUP A - Total nodes']
        df.loc[idx, 'GROUP A - Total edges'] = df.loc[idx - 1, 'GROUP A - Total edges']
        df.loc[idx, 'GROUP A - Average degree'] = df.loc[idx - 1, 'GROUP A - Average degree']
        df.loc[idx, 'GROUP A - Average degree centrality'] = df.loc[idx - 1, 'GROUP A - Average degree centrality']
        df.loc[idx, 'GROUP A - Average closeness'] = df.loc[idx - 1, 'GROUP A - Average closeness']
        # df.loc[idx, 'GROUP A - Average betweenness'] = df.loc[idx-1, 'GROUP A - Average betweenness']
        df.loc[idx, 'GROUP A - Average degree connectivity'] = df.loc[idx - 1, 'GROUP A - Average degree connectivity']
        df.loc[idx, 'GROUP A - Average assortativity'] = df.loc[idx - 1, 'GROUP A - Average assortativity']
        df.loc[idx, 'GROUP A - Average node connectivity'] = df.loc[idx - 1, 'GROUP A - Average node connectivity']
        df.loc[idx, 'GROUP A - Number of components'] = df.loc[idx - 1, 'GROUP A - Number of components']
        df.loc[idx, 'GROUP A - Number of strong components'] = df.loc[idx - 1, 'GROUP A - Number of strong components']
        # df.loc[idx, 'GROUP A - Shortest path'] = df.loc[idx-1, 'GROUP A - Shortest path']
        df.loc[idx, 'GROUP A - Centrality entropy'] = df.loc[idx - 1, 'GROUP A - Centrality entropy']
        df.loc[idx, 'GROUP A - Closeness entropy'] = df.loc[idx - 1, 'GROUP A - Closeness entropy']
        df.loc[idx, 'GROUP A - Sparseness'] = df.loc[idx - 1, 'GROUP A - Sparseness']

        df.loc[idx, 'GROUP B - Total classes'] = df.loc[idx - 1, 'GROUP B - Total classes']
        df.loc[idx, 'GROUP B - Total properties'] = df.loc[idx - 1, 'GROUP B - Total properties']
        # df.loc[idx, 'GROUP B - Total instances']  = df.loc[idx - 1, 'GROUP B - Total instances']
        # df.loc[idx, 'GROUP B - Total object properties']  = df.loc[idx - 1, 'GROUP B - Total object properties']
        # df.loc[idx, 'GROUP B - Total data properties']  = df.loc[idx - 1, 'GROUP B - Total data properties']
        # df.loc[idx, 'GROUP B - Total equivalent class properties']  = df.loc[idx - 1, 'GROUP B - Total equivalent class properties']
        # df.loc[idx, 'GROUP B - Total subclass properties']  = df.loc[idx - 1, 'GROUP B - Total subclass properties']
        # df.loc[idx, 'GROUP B - Total entities']  = df.loc[idx - 1, 'GROUP B - Total entities']
        # df.loc[idx, 'GROUP B - Total inverse entities']  = df.loc[idx - 1, 'GROUP B - Total inverse entities']
        # df.loc[idx, 'GROUP B - Ratio of inverse relations']  = df.loc[idx - 1, 'GROUP B - Ratio of inverse relations']
        # df.loc[idx, 'GROUP B - Property class ratio']  = df.loc[idx - 1, 'GROUP B - Property class ratio']
        df.loc[idx, 'GROUP B - Average population'] = df.loc[idx - 1, 'GROUP B - Average population']
        # df.loc[idx, 'GROUP B - Class property ratio']  = df.loc[idx - 1, 'GROUP B - Class property ratio']
        df.loc[idx, 'GROUP B - Attribute richness'] = df.loc[idx - 1, 'GROUP B - Attribute richness']
        # df.loc[idx, 'GROUP B - Inheritance richness']  = df.loc[idx - 1, 'GROUP B - Inheritance richness']
        df.loc[idx, 'GROUP B - Relationship richness'] = df.loc[idx - 1, 'GROUP B - Relationship richness']
        # df.loc[idx, 'GROUP B - Object properties ratio']  = df.loc[idx - 1, 'GROUP B - Object properties ratio']
        # df.loc[idx, 'GROUP B - Datatype properties ratio']  = df.loc[idx - 1, 'GROUP B - Datatype properties ratio']
        # df.loc[idx, 'GROUP B - Total concept assertions']  = df.loc[idx - 1, 'GROUP B - Total concept assertions']
        # df.loc[idx, 'GROUP B - Total role assertions']  = df.loc[idx - 1, 'GROUP B - Total role assertions']
        # df.loc[idx, 'GROUP B - Total general concept inclusions']  = df.loc[idx - 1, 'GROUP B - Total general concept inclusions']
        # df.loc[idx, 'GROUP B - Total domain axioms']  = df.loc[idx - 1, 'GROUP B - Total domain axioms']
        # df.loc[idx, 'GROUP B - Total range axioms']  = df.loc[idx - 1, 'GROUP B - Total range axioms']
        # df.loc[idx, 'GROUP B - Total role inclusions']  = df.loc[idx - 1, 'GROUP B - Total role inclusions']
        df.loc[idx, 'GROUP B - Total axioms'] = df.loc[idx - 1, 'GROUP B - Total axioms']
        # df.loc[idx, 'GROUP B - Total aBox axioms']  = df.loc[idx - 1, 'GROUP B - Total aBox axioms']
        # df.loc[idx, 'GROUP B - Total tBox axioms']  = df.loc[idx - 1, 'GROUP B - Total tBox axioms']

        df.loc[idx, 'GROUP C - Total triples'] = df.loc[idx - 1, 'GROUP C - Total triples']
        df.loc[idx, 'GROUP C - Total world instances'] = df.loc[idx - 1, 'GROUP C - Total world instances']
        df.loc[idx, 'GROUP C - Total claims'] = df.loc[idx - 1, 'GROUP C - Total claims']
        df.loc[idx, 'GROUP C - Total perspectives'] = df.loc[idx - 1, 'GROUP C - Total perspectives']
        df.loc[idx, 'GROUP C - Total mentions'] = df.loc[idx - 1, 'GROUP C - Total mentions']
        df.loc[idx, 'GROUP C - Total conflicts'] = df.loc[idx - 1, 'GROUP C - Total conflicts']
        df.loc[idx, 'GROUP C - Total sources'] = df.loc[idx - 1, 'GROUP C - Total sources']
        df.loc[idx, 'GROUP C - Total interactions'] = df.loc[idx, 'GROUP C - Total interactions']
        df.loc[idx, 'GROUP C - Total utterances'] = df.loc[idx - 1, 'GROUP C - Total utterances']

        df.loc[idx, 'GROUP C - Ratio claim to triples'] = df.loc[idx - 1, 'GROUP C - Ratio claim to triples']
        df.loc[idx, 'GROUP C - Ratio perspectives to triples'] = df.loc[
            idx - 1, 'GROUP C - Ratio perspectives to triples']
        df.loc[idx, 'GROUP C - Ratio conflicts to triples'] = df.loc[idx - 1, 'GROUP C - Ratio conflicts to triples']
        df.loc[idx, 'GROUP C - Ratio perspectives to claims'] = df.loc[
            idx - 1, 'GROUP C - Ratio perspectives to claims']
        df.loc[idx, 'GROUP C - Ratio mentions to claims'] = df.loc[idx - 1, 'GROUP C - Ratio mentions to claims']
        df.loc[idx, 'GROUP C - Ratio conflicts to claims'] = df.loc[idx - 1, 'GROUP C - Ratio conflicts to claims']

        df.loc[idx, 'GROUP C - Average perspectives per claim'] = df.loc[
            idx - 1, 'GROUP C - Average perspectives per claim']
        df.loc[idx, 'GROUP C - Average mentions per claim'] = df.loc[idx - 1, 'GROUP C - Average mentions per claim']
        df.loc[idx, 'GROUP C - Average turns per interaction'] = df.loc[
            idx - 1, 'GROUP C - Average turns per interaction']
        df.loc[idx, 'GROUP C - Average claims per source'] = df.loc[idx - 1, 'GROUP C - Average claims per source']
        df.loc[idx, 'GROUP C - Average perspectives per source'] = df.loc[
            idx - 1, 'GROUP C - Average perspectives per source']

        return df

    @staticmethod
    def _save(df, evaluation_folder):

        df = df.drop(columns=['Speaker', 'Response', 'rdf_file'])
        df.to_csv(evaluation_folder / 'graph_evaluation.csv', index=False)

    def plot_metrics_progression(self, metrics, convo_dfs, evaluation_folder):
        # Plot metrics progression per conversation
        for metric in metrics:
            metric_df = pd.DataFrame()

            # Iterate conversations
            for idx, convo_df in enumerate(convo_dfs):
                conversation_id = f'Conversation {idx}'
                convo_df = convo_df.set_index('Turn')

                # Add into a dataframe
                if len(metric_df) == 0:
                    metric_df[conversation_id] = convo_df[metric]
                else:
                    metric_df = pd.concat([metric_df, convo_df[metric]], axis=1)
                    metric_df.rename(columns={metric: conversation_id}, inplace=True)

            # Cutoff and plot
            self.plot_progression(metric_df, metric, evaluation_folder)

    @staticmethod
    def plot_progression(df_to_plot, xlabel, evaluation_folder):
        df_to_plot = df_to_plot.reset_index().melt('Turn', var_name='cols', value_name=xlabel)

        g = sns.relplot(x="Turn", y=xlabel, hue='cols', data=df_to_plot, kind='line')

        ax = plt.gca()
        plt.xlim(0)
        plt.xticks(ax.get_xticks()[::5], rotation="045")

        plot_file = evaluation_folder / f"{xlabel}.png"
        print(plot_file)

        g.figure.savefig(plot_file, dpi=300)
