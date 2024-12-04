import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from cltl.dialogue_evaluation.api import BasicPlotter

GRAPH_METRICS = ['GROUP A - Total nodes', 'GROUP A - Total edges', 'GROUP A - Average degree',
                 'GROUP A - Average degree centrality', 'GROUP A - Average closeness',
                 'GROUP A - Average betweenness',
                 'GROUP A - Average degree connectivity', 'GROUP A - Average assortativity',
                 'GROUP A - Average node connectivity', 'GROUP A - Number of components',
                 'GROUP A - Number of strong components', 'GROUP A - Shortest path', 'GROUP A - Centrality entropy',
                 'GROUP A - Closeness entropy', 'GROUP A - Sparseness',
                 'GROUP B - Total classes', 'GROUP B - Total properties', 'GROUP B - Total instances',
                 'GROUP B - Total object properties', 'GROUP B - Total data properties',
                 'GROUP B - Total equivalent class properties', 'GROUP B - Total subclass properties',
                 'GROUP B - Total inverse entities', 'GROUP B - Ratio of inverse relations',
                 'GROUP B - Property class ratio', 'GROUP B - Average population', 'GROUP B - Class property ratio',
                 'GROUP B - Attribute richness', 'GROUP B - Inheritance richness', 'GROUP B - Relationship richness',
                 'GROUP B - Object properties ratio', 'GROUP B - Datatype properties ratio',
                 'GROUP B - Total role assertions', 'GROUP B - Total general concept inclusions',
                 'GROUP B - Total domain axioms', 'GROUP B - Total range axioms', 'GROUP B - Total role inclusions',
                 'GROUP B - Total axioms', 'GROUP B - Total aBox axioms', 'GROUP B - Total tBox axioms',
                 'GROUP C - Total triples', 'GROUP C - Total world instances', 'GROUP C - Total claims',
                 'GROUP C - Total perspectives', 'GROUP C - Total mentions', 'GROUP C - Total conflicts',
                 'GROUP C - Total sources', 'GROUP C - Total interactions', 'GROUP C - Total utterances',
                 'GROUP C - Ratio claim to triples', 'GROUP C - Ratio perspectives to triples',
                 'GROUP C - Ratio conflicts to triples', 'GROUP C - Ratio perspectives to claims',
                 'GROUP C - Ratio mentions to claims', 'GROUP C - Ratio conflicts to claims',
                 'GROUP C - Average perspectives per claim', 'GROUP C - Average mentions per claim',
                 'GROUP C - Average turns per interaction', 'GROUP C - Average claims per source',
                 'GROUP C - Average perspectives per source'
                 ]

LIKELIHOOD_METRICS = ["MLM response", "System llh", "MLM llh"]


class Plotter(BasicPlotter):
    def __init__(self):
        """Creates an evaluator that will use graph metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        super(Plotter, self).__init__()
        self._log.debug(f"Plotter ready")

    def plot_conversations(self, scenarios_path, metrics):
        scenarios_paths = sorted([path for path in scenarios_path.iterdir() if path.is_dir() and path.stem != '.idea'])

        # Plot metrics progression per conversation
        for metric in metrics:
            metric_df = pd.DataFrame()

            # Read data
            for scenario in scenarios_paths:
                filename = 'graph_evaluation.csv' if metric in GRAPH_METRICS else 'likelihood_evaluation_context300.csv'

                convo_df = pd.read_csv(scenario / 'evaluation' / filename, header=0, sep=',')
                convo_df = convo_df.set_index('Turn')
                convo_df['Conversation'] = scenario.stem
                conversation_id = f"{convo_df['Conversation'].values[0]}"

                # Add into a dataframe
                if len(metric_df) == 0:
                    metric_df[conversation_id] = convo_df[metric]
                else:
                    metric_df = pd.concat([metric_df, convo_df[metric]], axis=1)
                    metric_df.rename(columns={metric: conversation_id}, inplace=True)

            # Cutoff and plot
            self.plot_progression(metric_df, metric, scenarios_path)

    @staticmethod
    def plot_progression(df_to_plot, xlabel, evaluation_folder):
        # Re-structure
        df_to_plot = df_to_plot.reset_index().melt('Turn', var_name='cols', value_name=xlabel)

        # Plot
        g = sns.relplot(x="Turn", y=xlabel, hue='cols', data=df_to_plot, kind='line')
        ax = plt.gca()
        plt.xlim(0)
        plt.xticks(ax.get_xticks()[::5], rotation=45)

        # Save
        plot_file = evaluation_folder / f"{xlabel}.png"
        print(plot_file)
        g.figure.savefig(plot_file, dpi=300, bbox_inches='tight')
