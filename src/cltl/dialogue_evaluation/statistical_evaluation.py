from pathlib import Path
from collections import Counter
import pandas as pd
import glob
from os import path
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

    def get_statistics_from_signals(self, signals):

        # TODO: fix next line, it's broken
        type_counts = {}
        type_dict_text, nr_annotations = self._get_annotation_dict(signals)

        for annoType in type_dict_text.keys():
            timedValues = type_dict_text.get(annoType)
            valueList = []
            for value in timedValues:
                valueList.append(self._get_get_value_from_annotation(value[1]))
            type_counts[annoType]=Counter(valueList)

        return type_counts, type_dict_text, nr_annotations

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

    def get_turn_stats(self, turns):
        average_tokens_per_turn = 0
        average_turn_length = 0
        average_token_length = 0
        for turn in turns:
            tokens = turn[1].split(" ")
            average_turn_length += len(turn[1])
            average_tokens_per_turn += len(tokens)
            for token in tokens:
                average_token_length += len(token)

        average_token_length = average_token_length/ average_tokens_per_turn
        average_tokens_per_turn = average_tokens_per_turn/len(turns)
        average_turn_length = average_turn_length/len(turns)
        return average_turn_length, average_tokens_per_turn, average_token_length

    def get_overview_statistics(self, scenario_folder):
        stat_dict = {}
        columns = ["Label"]
        for f in glob.glob(scenario_folder+"/*/"+"evaluation/"+"*_meta_data.csv", recursive=True):
            file = open(f, 'r')
          #  print(file.name)
            scenario = file.name
            columns.append(scenario)
            lines = [x.strip() for x in file.readlines()]
            anno_type = "General"
            scenario_dict = {}
            if anno_type in stat_dict:
                scenario_dict = stat_dict.get(anno_type)
            for fields in lines:
                # print(fields)
                if type(fields) == str:
                    fields = fields.split('\t')
                if len(fields) == 1 and len(fields[0]) > 0:
                    ### we are getting a new type of annotation
                    # print("Saving the current data for:", anno_type)
                    stat_dict[anno_type] = scenario_dict
                    anno_type = fields[0]
                    # print("Getting data for the new anno_type:[", anno_type, "]", fields)
                    if anno_type in stat_dict:
                        scenario_dict = stat_dict.get(anno_type)
                    else:
                        scenario_dict = {}
                elif len(fields) == 2:
                    col = fields[0]
                    value = fields[1]
                    # print(anno_type, 'col', col, 'value', value)
                    if col in scenario_dict:
                        scenario_dict[col].append((scenario, value))
                    else:
                        scenario_dict[col] = [(scenario, value)]
                else:
                    print('Error nr. of fields:', len(fields), fields)
                    continue
            return stat_dict, columns

    def save_overview_statistics(self, scenario_folder, stat_dict, columns):
        for key in stat_dict.keys():
            dfall = pd.DataFrame(columns=columns)
            anno_dict = stat_dict.get(key)
            for anno in anno_dict.keys():
                values = anno_dict.get(anno)
                row = {'Label': anno}
                for value in values:
                    scenario = value[0]
                    count = value[1]
                    row.update({scenario: count})
                dfall = dfall.append(row, ignore_index=True)
            file_path = scenario_folder+"/"+key+".csv"
            dfall.to_csv(file_path)

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

        #### Text signals statistics
        meta+="\nText signals\n"
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, turns, speakers = text_util.get_turns_with_context_from_signals(text_signals)
        meta+='NR. TURNS\t'+ str(len(turns))+"\n"
        average_turn_length, average_tokens_per_turn, average_token_length = self.get_turn_stats(turns)
        meta+='Average turn length\t' + str(average_turn_length)+'\n'
        meta+='Average nr. tokens per turn\t' + str(average_tokens_per_turn)+'\n'
        meta+='Average token length\t' + str(average_token_length)+'\n'
        meta+='SPEAKER SET\t'+ str(speakers)+"\n"

        text_type_counts, text_type_timelines, nr_annotations = self.get_statistics_from_signals(text_signals)
       # rows.extend(self.get_statistics_from_image_annotation(scenario_ctrl, scenario_id))
        meta+='TOTAL ANNOTATIONS\t'+ str(nr_annotations)+"\n"
        meta+="\n"
        for key in text_type_counts.keys():
            counts = text_type_counts.get(key)
            meta+= key+'\n'
            for item in counts:
                meta+=item+"\t"+str(counts.get(item))+"\n"


        meta+="\nImage signals\n"

        image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
        text_type_counts, text_type_timelines, nr_annotations = self.get_statistics_from_signals(image_signals)
        meta += 'TOTAL ANNOTATIONS\t' + str(nr_annotations) + "\n"
        meta += "\n"
        for key in text_type_counts.keys():
            counts = text_type_counts.get(key)
            meta += key + '\n'
            for item in counts:
                meta += item + "\t" + str(counts.get(item)) + "\n"

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

    def _get_get_value_from_annotation(self, annotation):
        anno = ""
        #print(annotation)
        if isinstance(annotation, str):
            anno = "faceID:"+annotation
        else:
            try:
                # value is the correct python object
                value_dict = vars(annotation)
                anno = "label:" + value_dict
                #print('value_dict', value_dict)
            except:
                # value is a namedtuple
                try:
                    value_dict = annotation._asdict()
                    type = ""
                    value = ""
                    if "value" in value_dict:
                        value = value_dict['value']
                        if "type" in value_dict:
                            type= value_dict['type']
                    elif "label" in value_dict:
                        value = value_dict['label']
                        if "type" in value_dict:
                            type = value_dict['type']
                        elif "text" in value_dict:
                            type = value_dict['label']
                            value = value_dict['text']
                        else:
                            type = "label"
                    elif "type" in value_dict:
                        if "text" in value_dict:
                            type= value_dict['type']
                            value= value_dict['text']
                        else:
                            value = value_dict['type']
                            type = "label"
                    elif "pos" in value_dict:
                        value = value_dict['pos']
                        type = "pos"
                    # elif "label" in value_dict:
                    #     value = value_dict['label']
                    #     type = "entity"
                    else:
                        print('UNKNOWN annotation', annotation)
                    anno = type+":"+value
                except:
                    if annotation:
                        print('UNKNOWN annotation type', type(annotation), annotation)

        return anno



    def _save(self, df, evaluation_folder, scenario_id):
        file_name =  scenario_id+"_statistical_analysis.csv"
        df.to_csv(evaluation_folder / file_name, index=False)


#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='GO', confidence=0.7935183048248291, value='anger'),
#Annotation(type='python-type:cltl.dialogue_act_classification.api.DialogueAct', value=JSON(type='MIDAS', confidence=3.6899490356445312, value='opinion'),
#Annotation(type='ConversationalAgent', value='SPEAKER', source='LEOLANI', timestamp=1665746858876)
#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='SENTIMENT', confidence=0.9314287331653759, value='negative'), source='python-source:cltl.emotion_extraction.utterance_go_emotion_extractor', timestamp=1665746860001)
