from pathlib import Path
from collections import Counter
import pandas as pd
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality

import cltl.dialogue_evaluation.utils.text_signal as text_util
import cltl.dialogue_evaluation.utils.image_signal as image_util
from emissor.representation.scenario import Signal

from cltl.dialogue_evaluation.api import BasicEvaluator


class StatisticalEvaluator(BasicEvaluator):
    def __init__(self):
        """Creates an evaluator that will calculate basic statistics for evaluation
        params
        returns: None
        """
        super(StatisticalEvaluator, self).__init__()

        self._log.debug(f"Statistical Evaluator ready")

    def get_statistics_from_text_annotation(self, scenario_ctrl, scenario_id):

        # TODO: fix next line, it's broken
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, turns, speakers = text_util.get_turns_with_context_from_signals(text_signals)

        print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)
        print('Speakers:', speakers)

        type_dict_text, id_dict_text = self._get_annotation_dict(text_signals)

        type_rows = self._get_stats_from_text_dict(type_dict_text)
        value_rows = self._get_stats_from_text_dict(id_dict_text)
        return type_rows, value_rows

    def get_statistics_from_image_annotation(self, scenario_ctrl, scenario_id):

        image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
        print('Nr of perceptions:', len(image_signals), ' extracted from scenarion: ', scenario_id)

        type_dict_image, id_dict_text = self._get_annotation_dict(image_signals)
        type_rows = self._get_stats_from_text_dict(type_dict_image)
        value_rows = self._get_stats_from_text_dict(id_dict_text)
        return type_rows, value_rows

    def analyse_interaction(self, scenario_folder, scenario_id, metrics_to_plot=None):
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        scenario_storage = ScenarioStorage(scenario_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        print('SCENARIO_FOLDER:', scenario_folder)
        print('SCENARIO_ID:', scenario_id)

        text_type_rows, text_id_rows = self.get_statistics_from_text_annotation(scenario_ctrl, scenario_id)
       # rows.extend(self.get_statistics_from_image_annotation(scenario_ctrl, scenario_id))

        # Get likelihood scored
        # speaker_turns = {k: [] for k in speakers}
        #df = self._calculate_metrics(turns, speaker_turns)

        #@TODO make a nicer table
        df = pd.DataFrame(text_id_rows)
        # Save
        evaluation_folder = Path(scenario_folder + '/' + scenario_id + '/evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(df, evaluation_folder, scenario_id)


    def _get_annotation_dict (self, signals:[Signal]):
            all_annotations = []
            type_dict = {}
            id_dict = {}
            time_dict = {}
            for signal in signals:
                mentions = signal.mentions
                id = signal.id
                timestamp = signal.time.start
                for mention in mentions:
                    annotations = mention.annotations
                    all_annotations.append((timestamp, annotations))

            print('Annotations:', len(all_annotations))
            # for a in all_annotations:
            #     print(a)
            for pair in all_annotations:
                id_key = pair[0]
                anno = pair[1]
                type_key = anno[0].type
                value = anno[0].value
                if not type_key=='Face' and not type_key==None:
                   # print('type', type_key)
                    if not type_dict.get(type_key):
                        type_dict[type_key] = [(id_key, value)]
                    else:
                        type_dict[type_key].append((id_key, value))
                    if not id_dict.get(id_key):
                        id_dict[id_key] = [(type_key, value)]
                    else:
                        id_dict[id_key].append((type_key, value))
            return type_dict, id_dict

    def _get_stats_from_image_dict(self, dict: {}):
        # Iterate turns
        rows = []
        for key in dict:
         #   print('key', key)
            if not key=='python-type:builtins.NoneType':
                annotations = dict.get(key)
                value_list = []
                for key, annotation in annotations:
                    # if isinstance(value, [str, int, bool]):
                    if isinstance(annotation, str):
                        value_list.append(annotation)
                    else:
                        try:
                            # value is the correct python object
                            value_dict = vars(annotation)
                            print('value_dict', value_dict)
                        except:
                            # value is a namedtuple
                            value_dict = annotation._asdict()
                            if "value" in value_dict:
                                value_list.append(value_dict['value'])
                            elif "type" in value_dict:
                                value_list.append(value_dict['type'])
                            elif "pos" in value_dict:
                                value_list.append(value_dict['pos'])
                    counts = Counter(value_list)
                    print(key, counts)
                    rows.append([key, value_list])

        return rows

    def _get_stats_from_text_dict(self, dict: {}):
        # Iterate turns
        rows = []
        for key in dict:
            annotations = dict.get(key)
            value_list = []
            for key, annotation in annotations:
                #if isinstance(value, [str, int, bool]):
                if isinstance(annotation, str):
                    value_list.append(annotation)
                else:
                    try:
                        # value is the correct python object
                        value_dict = vars(annotation)
                        print('value_dict', value_dict)
                    except:
                        # value is a namedtuple
                        value_dict = annotation._asdict()
                        if "value" in value_dict:
                            value_list.append(value_dict['value'])
                        elif "type" in value_dict:
                            value_list.append(value_dict['type'])
                        elif "pos" in value_dict:
                            value_list.append(value_dict['pos'])
                counts = Counter(value_list)
                print(key, counts)
                rows.append([key, counts.items()])
        return rows


    @staticmethod
    def _calculate_metrics(turns, speaker_turns):
        # Iterate turns
        rows = []
        for index, turn in enumerate(turns):
            # TODO count things here (e.g. entities mentioned,
            pass

        return pd.DataFrame(rows)

    def _save(self, df, evaluation_folder, scenario_id):
        file_name =  scenario_id+"statistical_analysis.csv"
        df.to_csv(evaluation_folder / file_name, index=False)


#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='GO', confidence=0.7935183048248291, value='anger'),
#Annotation(type='python-type:cltl.dialogue_act_classification.api.DialogueAct', value=JSON(type='MIDAS', confidence=3.6899490356445312, value='opinion'),
#Annotation(type='ConversationalAgent', value='SPEAKER', source='LEOLANI', timestamp=1665746858876)
#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='SENTIMENT', confidence=0.9314287331653759, value='negative'), source='python-source:cltl.emotion_extraction.utterance_go_emotion_extractor', timestamp=1665746860001)
