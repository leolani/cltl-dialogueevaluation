import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from cltl.dialogue_evaluation.api import BasicCorrelator


class Correlator(BasicCorrelator):
    def __init__(self):
        """Creates an evaluator that will use graph metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        super(Correlator, self).__init__()
        self._log.debug(f"Correlator ready")

    def correlate_metrics(self, scenarios_path, metrics):
        scenarios_paths = sorted([path for path in scenarios_path.iterdir()
                                  if path.is_dir() and path.stem not in ['.idea', 'plots']])

        corr_dfs = []
        for scenario in scenarios_paths:
            # Read data from human annotations, automatic and likelihood
            convo_df = self.read_evaluations(scenario, metrics)
            # convo_df = convo_df.set_index('Turn')
            convo_df['Conversation'] = scenario.stem
            conversation_id = f"{convo_df['Conversation'].values[0]}"

            # Compute correlations
            corr_df = convo_df.corr(method='pearson', numeric_only=True)
            corr_dfs.append(corr_df)

            # Plot per scenario
            self.plot_correlations(corr_df, None, conversation_id, scenarios_path)

        # Average conversations
        avg_df = pd.concat(corr_dfs).groupby(level=0).mean(numeric_only=True)
        avg_df = avg_df.reindex(sorted(avg_df.columns), axis=1)
        self.plot_correlations(avg_df, None, '', scenarios_path)

    @staticmethod
    def read_evaluations(scenario, metrics):
        print(f"Correlations on {scenario.stem}")

        # Read evaluations
        evaluations = []
        for file in ['graph_evaluation.csv', 'likelihood_evaluation_context300.csv',
                     f'{scenario.stem}_manual_evaluation.csv']:
            try:
                df = pd.read_csv(scenario / 'evaluation' / file, header=0, index_col='Turn')
            except:
                try:
                    df = pd.read_csv(scenario / 'evaluation' / file, header=0, index_col='Turn', sep=';')
                except:
                    print(f"Could not load {scenario}")
                    df = pd.DataFrame()
                    # continue

            columns_to_keep = [c for c in metrics if c in df.columns]
            df = df[columns_to_keep]
            evaluations.append(df)

        # Merge and select
        full_df = pd.concat(evaluations, axis=1)

        # rename
        full_df.rename(columns={'System llh': 'AUTOMATIC - System llh', 'MLM llh': 'AUTOMATIC - MLM llh',
                                'USR DLcontext': 'AUTOMATIC - USR DLcontext', 'USR DLfact': 'AUTOMATIC - USR DLfact'},
                       inplace=True)
        full_df.rename(columns={'Overall Human Rating': 'HUMAN - Overall Human Rating',
                                'Interesting': 'HUMAN - Interesting', 'Engaging': 'HUMAN - Engaging',
                                'Specific': 'HUMAN - Specific', 'Relevant': 'HUMAN - Relevant',
                                'Correct': 'HUMAN - Correct',
                                'Semantically Appropriate': 'HUMAN - Semantically Appropriate',
                                'Understandable': 'HUMAN - Understandable',
                                'Fluent': 'HUMAN - Fluent'}, inplace=True)

        return full_df

    @staticmethod
    def plot_correlations(df_to_plot, mask, name, evaluation_folder):
        # Plot
        plt.figure()
        plt.xticks(fontsize=3)
        plt.yticks(fontsize=3)

        g = sns.heatmap(df_to_plot, mask=mask, annot=False, fmt=".2f",
                        cmap="YlGnBu", cbar_kws={"shrink": .3, "location": "top"},
                        cbar=True, center=0,
                        square=True)

        # Save
        plot_file = evaluation_folder / name / 'plots'
        plot_file.mkdir(parents=True, exist_ok=True)
        g.figure.savefig(plot_file / f"Correlation heatmap.png", dpi=300, transparent=False, bbox_inches='tight')
        plt.close()
        print(f"\tSaved to file: {plot_file}")
