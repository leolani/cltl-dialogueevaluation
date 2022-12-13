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


    def get_manual_evaluation_overview(self, scenario_folder):
        stat_dict = {}

        storage = ScenarioStorage(scenario_folder)
        scenarios = list(storage.list_scenarios())
        print("Processing scenarios: ", scenarios)
        columns = ["Label"]

        for scenario in scenarios:
            columns.append(scenario)
           # csv_path = scenario_folder+"/"+scenario+"/"+"evaluation/"+scenario+"_manual_evaluation.csv"
            csv_path = scenario_folder+"/"+scenario+"/"+"evaluation/"+scenario+"_manual_evaluation.csv"
            print('Reading', csv_path)
            try:
                df = pd.read_csv(csv_path)
            except:
                df = pd.read_csv(csv_path, sep=";")
            overall = 0;
            interesting = 0
            engaging = 0
            specific = 0
            relevant = 0
            correct = 0;
            appropriate = 0
            understandable = 0
            fluent = 0
            agent = 'LEOLANI'
            agent_turns =0
            for index in df.index:
                if not df['Speaker'][index]==agent:
                  #  print(df['Speaker'][index])
                    continue
                scored = False
                if df["Overall Human Rating"][index]:
                    value = df["Overall Human Rating"][index]
                    #if type(value)=='float' or type(value)=='numpy.float64':
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            overall += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Interesting"][index]:
                    value = df["Interesting"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            interesting += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Engaging"][index]:
                    value = df["Engaging"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            engaging += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Specific"][index]:
                    value = df["Specific"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            specific += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Relevant"][index]:
                    value = df["Relevant"][index]
                    if not value == 'nan' and not value == '-':
                        if type(value == 'str'):
                            relevant += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Correct"][index]:
                    value = df["Correct"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            correct += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Semantically Appropriate"][index]:
                    value = df["Semantically Appropriate"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            appropriate += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Understandable"][index]:
                    value = df["Understandable"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            understandable += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if df["Fluent"][index]:
                    value = df["Fluent"][index]
                    if not value=='nan' and not value=='-':
                        if type(value=='str'):
                            fluent += float(value)
                        else:
                            overall += value
                        scored = True
                    else:
                        print(type(value))
                if scored:
                    agent_turns += 1
            #### After for loop
            if agent_turns>0:
                row = {"Overall_Rating":overall/agent_turns,"Interesting": interesting/agent_turns,
                       "Engaging": engaging/agent_turns,"Specific": specific/agent_turns,"Relevant": relevant/agent_turns,
                       "Correct": correct/agent_turns,"Semantically_Appropriate":appropriate/agent_turns,
                       "Understandable":understandable/agent_turns,"Fluent":fluent/agent_turns}
                print(row)
                stat_dict[scenario] = row
            #break
        return stat_dict, columns

    def save_manual_evaluations(self, scenario_folder, stat_dict, columns):
        #  Rows:
        rows = ["Overall_Rating","Interesting","Engaging","Specific","Relevant","Correct","Semantically_Appropriate","Understandable","Fluent"]
        dfall = pd.DataFrame(columns=columns)
        turn_row = {'Label': 'Turns'}
        image_row = {'Label': 'Images'}
        storage = ScenarioStorage(scenario_folder)
        scenarios = list(storage.list_scenarios())
        for scenario in scenarios:
            scenario_ctrl = storage.load_scenario(scenario)
            text_signals = scenario_ctrl.get_signals(Modality.TEXT)
            image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
            turn_row.update({scenario: len(text_signals)})
            image_row.update({scenario: len(image_signals)})

        dfall = dfall.append(turn_row, ignore_index=True)
        dfall = dfall.append(image_row, ignore_index=True)

        for label in rows:
            row = {'Label': label}
            for scenario in scenarios:
               # print(label, scenario)
                if scenario in stat_dict.keys():
                    count_dict = stat_dict.get(scenario)
                    if label in count_dict.keys():
                        count = count_dict[label]
                    else:
                        count = 0
                else:
                   count = 0
                row.update({scenario: count})
            print(row)
            dfall = dfall.append(row, ignore_index=True)

        file_path = scenario_folder + "/" + "manual_evaluation_overview.csv"
        print("Saving overview to:", file_path)
        dfall.to_csv(file_path)