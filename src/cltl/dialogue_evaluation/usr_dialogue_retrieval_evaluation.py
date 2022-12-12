from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality

import cltl.dialogue_evaluation.utils.text_signal as text_util
from cltl.dialogue_evaluation.api import BasicEvaluator
from cltl.dialogue_evaluation.metrics.utterance_usr_dialog_retrieval import USR_CTX


class USR_DialogRetrieval_Evaluator(BasicEvaluator):
    def __init__(self, model_path_ctx, context_type, max_context=300, len_top_tokens=20):
        """Creates an evaluator that will use USR Masked Language Model scoring to approximate the quality of a conversation, across turns.

        We use the Roberta model that was pretrained with the TopicalChat data by the USR team
        as a model for gettting the averaged token likelihood of the target sentence.
        The function *sentence_likelihood* also returns the most likley sentence according to the model
        and the averaged score for the mostly likely tokens.
        We can thus compare the actual response in a turn with the response that would be generated by the LM.

        The LM will return a number of results for the masked token with probability scores.
        We compare the target token with the results to get the score for the target token.
        If the target token is not in the results, we set the probability to "0".

        You can set the number of results returned by the model.
        The more results, the more likely the target gets a score, albeit a very low score.
        params
        model_path_mlm: one of ['adamlin/usr-topicalchat-roberta_ft', 'xlm-roberta-base', 'roberta-base']
        returns: None
        """
        super(USR_DialogRetrieval_Evaluator, self).__init__()
        self.model_path_mlm = model_path_ctx
        self.max_context = max_context
        self.len_top_tokens = len_top_tokens
        self.context = context_type
        # Create MLM
        self.model_ctx = USR_CTX(path=self.model_path_mlm)

        self._log.debug(f"Likelihood Evaluator ready")

    def evaluate_conversation(self, scenario_folder, scenario_id, metrics_to_plot=None):
        # Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        scenario_storage = ScenarioStorage(scenario_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, turns, speakers = text_util.get_turns_with_context_from_signals(signals, self.max_context)

        print('SCENARIO_FOLDER:', scenario_folder)
        print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)
        print('Speakers:', speakers)
        print('Max context:', self.max_context)

        # Get likelihood scored
        speaker_ctx_scores = {k: [] for k in speakers}
        speaker_turns = {k: [] for k in speakers}

        df = self._calculate_metrics(self.model_ctx, turns, speaker_ctx_scores, speaker_turns)
        avg_df = self._average_metrics(speakers, turns, speaker_ctx_scores)

        # Save
        evaluation_folder = Path(scenario_folder / scenario_id / 'evaluation')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(df, avg_df, evaluation_folder)
        #
        if metrics_to_plot:
            self.plot_metrics_progression(metrics_to_plot, [df], evaluation_folder)

    @staticmethod
    def _calculate_metrics(model_ctx, turns, speaker_ctx_scores, speaker_turns):
        # Iterate turns
        print(f"\n\tCalculating likelihood scores")
        rows = []
        for index, turn in enumerate(turns):
            print(f"\t\tProcessing turn {index}/{len(turns)}")
            context = turn[0]
            target = turn[1]
            cue = turn[2]
            speaker = turn[3]
            score = model_ctx.MCtx(context, target)
            rows.append({"Turn": index, "Speaker": speaker, "Cue": cue, "Response": target, "Context": context,
                         "Ctx Score": score})

            if speaker:
                speaker_turns[speaker].append(index)
                speaker_ctx_scores[speaker].append(score)

        return pd.DataFrame(rows)

    @staticmethod
    def _average_metrics(speakers, turns, speaker_ctx_scores):
        # Iterate turns
        print(f"\n\tCalculating average USR Context scores")
        overall_rows = []
        for speaker in speakers:
            ctx_scores = speaker_ctx_scores[speaker]
            ctx_average_score = sum(ctx_scores) / len(ctx_scores)
            overall_rows.append({'Speaker': speaker, 'Nr. turns': len(turns), 'Ctx Avg': ctx_average_score})

        # Save
        return pd.DataFrame(overall_rows)

    def _save(self, df, avg_df, evaluation_folder):

        file = "usr_evaluation" + "_context_" + self.context + "_" + str(self.max_context) + ".csv"
        df.to_csv(evaluation_folder / file, index=False)

        file = "usr_evaluation" + "_context_" + self.context + "_" + str(self.max_context) + "_overall.csv"
        avg_df.to_csv(evaluation_folder / file, index=False)

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
            label = metric + "_" + self.context
            self.plot_progression(metric_df, label, evaluation_folder)

    @staticmethod
    def plot_progression(df_to_plot, xlabel, evaluation_folder):
        df_to_plot = df_to_plot.reset_index().melt('Turn', var_name='cols', value_name=xlabel)

        g = sns.relplot(x="Turn", y=xlabel, hue='cols', data=df_to_plot, kind='line')

        ax = plt.gca()
        plt.xlim(0)
        plt.xticks(ax.get_xticks()[::5], rotation=45)

        plot_file = evaluation_folder / f"{xlabel}.png"
        print(plot_file)

        g.figure.savefig(plot_file, dpi=300)
