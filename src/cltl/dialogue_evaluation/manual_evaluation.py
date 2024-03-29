from pathlib import Path

import pandas as pd
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality

import cltl.dialogue_evaluation.utils.text_signal as text_util
from cltl.dialogue_evaluation.api import BasicEvaluator


class ManualEvaluator(BasicEvaluator):
    def __init__(self):
        """Creates an evaluator that will create placeholders for manual evaluation
        params
        returns: None
        """
        super(ManualEvaluator, self).__init__()

        self._log.debug(f"Manual Evaluator ready")

    def evaluate_conversation(self, scenario_folder, scenario_id, metrics_to_plot=None):
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        scenario_storage = ScenarioStorage(scenario_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, turns, speakers = text_util.get_turns_with_context_from_signals(signals)

        print('SCENARIO_FOLDER:', scenario_folder)
        print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)
        print('Speakers:', speakers)

        # Get likelihood scored
        speaker_turns = {k: [] for k in speakers}

        df = self._calculate_metrics(turns, speaker_turns)

        # Save
        evaluation_folder = Path(scenario_folder + '/' + scenario_id + '/evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(df, evaluation_folder, scenario_id)
        self._create_dialogue_summary_file(evaluation_folder, scenario_id)
        #
        # if metrics_to_plot:
        #     self.plot_metrics_progression(metrics_to_plot, [full_df], evaluation_folder)

    @staticmethod
    def _calculate_metrics(turns, speaker_turns):
        # Iterate turns
        print(f"\tPlaceholders for manual scores")
        rows = []
        for index, turn in enumerate(turns):
            context = turn[0]
            target = turn[1]
            cue = turn[2]
            speaker = turn[3]
            rows.append({"Turn": index, "Speaker": speaker, "Cue": cue, "Response": target, "Reference Response": "", "Context": context,
                         "Overall Human Rating": '', "Interesting": '', "Engaging": '', "Specific": '', "Relevant": '',
                         "Correct": '', "Semantically Appropriate": '', "Understandable": '', "Fluent": ''})

            if speaker:
                speaker_turns[speaker].append(index)

        return pd.DataFrame(rows)

    def _save(self, df, evaluation_folder, scenario_id):
        file_name =  scenario_id+"_manual_evaluation.csv"
        df.to_csv(evaluation_folder / file_name, index=False)

    def _create_dialogue_summary_file(self, evaluation_folder, scenario_id):
        file_name =  scenario_id+"_dialogue_summary.txt"
       # Create an empty file for the dialogue summary
        with open(evaluation_folder / file_name, 'w') as fp:
            pass

    # def plot_metrics_progression(self, metrics, convo_dfs, evaluation_folder):
    #     # Plot metrics progression per conversation
    #     for metric in metrics:
    #         metric_df = pd.DataFrame()
    #
    #         # Iterate conversations
    #         for idx, convo_df in enumerate(convo_dfs):
    #             conversation_id = f'Conversation {idx}'
    #             convo_df = convo_df.set_index('Turn')
    #
    #             # Add into a dataframe
    #             if len(metric_df) == 0:
    #                 metric_df[conversation_id] = convo_df[metric]
    #             else:
    #                 metric_df = pd.concat([metric_df, convo_df[metric]], axis=1)
    #                 metric_df.rename(columns={metric: conversation_id}, inplace=True)
    #
    #         # Cutoff and plot
    #         self.plot_progression(metric_df, metric, evaluation_folder)
    #
    # @staticmethod
    # def plot_progression(df_to_plot, xlabel, evaluation_folder):
    #     df_to_plot = df_to_plot.reset_index().melt('Turn', var_name='cols', value_name=xlabel)
    #
    #     g = sns.relplot(x="Turn", y=xlabel, hue='cols', data=df_to_plot, kind='line')
    #
    #     ax = plt.gca()
    #     plt.xlim(0)
    #     plt.xticks(ax.get_xticks()[::5], rotation="045")
    #
    #     plot_file = evaluation_folder / f"{xlabel}.png"
    #     print(plot_file)
    #
    #     g.figure.savefig(plot_file, dpi=300)
