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

    def get_statistics_from_text_annotation(self, text_signals):

        # TODO: fix next line, it's broken
        type_counts = {}
        type_dict_text, nr_annotations = self._get_annotation_dict(text_signals)

        for annoType in type_dict_text.keys():
            timedValues = type_dict_text.get(annoType)
            valueList = []
            for value in timedValues:
                valueList.append(self._get_get_value_from_annotation(value[1]))
            type_counts[annoType]=Counter(valueList)

        return type_counts, type_dict_text, nr_annotations

    def get_statistics_from_image_annotation(self, scenario_ctrl, scenario_id):

        image_signals = scenario_ctrl.get_signals(Modality.IMAGE)

        type_dict_image, id_dict_text, nr_annotations = self._get_annotation_dict(image_signals)
        type_rows = self._get_stats_from_text_dict(type_dict_image)
        value_rows = self._get_stats_from_text_dict(id_dict_text)
        return type_rows, value_rows, nr_annotations

    def get_duration_in_minutes(self, scenario_ctrl):
        start = 0
        end = 0
        duration = 0
        try:
            start = int(scenario_ctrl.scenario.start)
            end = int(scenario_ctrl.scenario.end)
        except:
            print('Error getting duration')
            print('start', scenario_ctrl.scenario.start)
            print('end', scenario_ctrl.scenario.end)
        if start>0 and end>0:
            duration = (end - start) / 60000
        return duration

    def analyse_interaction(self, scenario_folder, scenario_id, metrics_to_plot=None):
        # Save
        evaluation_folder = Path(scenario_folder + '/' + scenario_id + '/evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)

        meta = ""
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        scenario_storage = ScenarioStorage(scenario_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        meta+='SCENARIO_FOLDER\t'+ scenario_folder+"\n"
        meta+='SCENARIO_ID\t'+ scenario_id+"\n"
        speaker = scenario_ctrl.scenario.context.speaker["name"]
        agent = scenario_ctrl.scenario.context.agent["name"]
        location = scenario_ctrl.scenario.context.location_id  #### Change this to location name when this implemented
        meta+='AGENT\t'+agent+'\n'
        meta+='SPEAKER\t'+speaker+'\n'
        meta+='LOCATION\t'+location+'\n'

        people = scenario_ctrl.scenario.context.persons
        objects = scenario_ctrl.scenario.context.objects
        meta+='PEOPLE SEEN\t'+str(people)+'\n'
        meta+='OBJECTS SEEN\t'+str(objects)+'\n'
        duration = self.get_duration_in_minutes(scenario_ctrl)
        meta+='DURATION IN MINUTES\t'+str(duration)+"\n"
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, turns, speakers = text_util.get_turns_with_context_from_signals(text_signals)
        meta+='NR. TURNS\t'+ str(len(turns))+"\n"
        meta+='SPEAKER SET\t'+ str(speakers)+"\n"

        text_type_counts, text_type_timelines, nr_annotations = self.get_statistics_from_text_annotation(text_signals)
       # rows.extend(self.get_statistics_from_image_annotation(scenario_ctrl, scenario_id))
        meta+='TOTAL ANNOTATIONS\t'+ str(nr_annotations)+"\n"
        meta+="\n"
        for key in text_type_counts.keys():
            counts = text_type_counts.get(key)
            meta+= key+'\n'
            for item in counts:
                meta+=item+"\t"+str(counts.get(item))+"\n"
        # testing
        print(meta)

        ## Save the meta data
        file_name = scenario_id + "_meta_data.csv"
        with open(evaluation_folder / file_name, 'w') as f:
            f.write(meta)

        # Get likelihood scored
        # speaker_turns = {k: [] for k in speakers}
        #df = self._calculate_metrics(turns, speaker_turns)

        #@TODO make a nicer table
        #df = pd.DataFrame(text_temp_rows)

        #self._save(df, evaluation_folder, scenario_id)


    def _get_annotation_dict (self, signals:[Signal]):
            all_annotations = []
            type_dict = {}
            for signal in signals:
                mentions = signal.mentions
                timestamp = signal.time.start
                for mention in mentions:
                    annotations = mention.annotations
                    all_annotations.append((timestamp, annotations))
            #print('ANNOTATIONS:', len(all_annotations))
            # for a in all_annotations:
            #     print(a)
            for pair in all_annotations:
                time_key = pair[0]
                anno = pair[1]
                if anno:
                    type_key = anno[0].type
                    value = anno[0].value
                    if not type_key=='Face' and not type_key==None:
                       # print('type', type_key)
                        #### create a dict with all values for each annotation type
                        if not type_dict.get(type_key):
                            type_dict[type_key] = [(time_key, value)]
                        else:
                            type_dict[type_key].append((time_key, value))
            return type_dict, len(all_annotations)

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
            for key, annotation in annotations:
                value_list = []
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
                #print(key, value_list)
                rows.append([key,value_list])
            #print(rows[:10])
        return rows

    def _get_get_value_from_annotation(self, annotation):
        anno = ""
        if isinstance(annotation, str):
            anno = "label:"+annotation
        else:
            try:
                # value is the correct python object
                value_dict = vars(annotation)
                anno = "label:" + value_dict
                #print('value_dict', value_dict)
            except:
                # value is a namedtuple
                value_dict = annotation._asdict()
                type = ""
                value = ""
                if "value" in value_dict:
                    value = value_dict['value']
                    if "type" in value_dict:
                        type= value_dict['type']
                elif "type" in value_dict:
                    value = value_dict['type']
                    type = "label"
                elif "pos" in value_dict:
                    value = value_dict['pos']
                    type = "pos"
                elif "label" in value_dict:
                    value = value_dict['label']
                    type = "entity"
                else:
                    print('UNKNOWN annotation', annotation)
                anno = type+":"+value
        return anno


    @staticmethod
    def _calculate_metrics(turns, speaker_turns):
        # Iterate turns
        rows = []
        for index, turn in enumerate(turns):
            # TODO count things here (e.g. entities mentioned,
            pass

        return pd.DataFrame(rows)

    def _save(self, df, evaluation_folder, scenario_id):
        file_name =  scenario_id+"_statistical_analysis.csv"
        df.to_csv(evaluation_folder / file_name, index=False)


#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='GO', confidence=0.7935183048248291, value='anger'),
#Annotation(type='python-type:cltl.dialogue_act_classification.api.DialogueAct', value=JSON(type='MIDAS', confidence=3.6899490356445312, value='opinion'),
#Annotation(type='ConversationalAgent', value='SPEAKER', source='LEOLANI', timestamp=1665746858876)
#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='SENTIMENT', confidence=0.9314287331653759, value='negative'), source='python-source:cltl.emotion_extraction.utterance_go_emotion_extractor', timestamp=1665746860001)
