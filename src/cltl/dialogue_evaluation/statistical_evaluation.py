import glob
import json
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
import cltl.dialogue_evaluation.utils.plot_interaction as plot
import cltl.dialogue_evaluation.utils.text_signal as text_util
#import cltl.dialogue_evaluation.utils.image_signal as image_util
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


    def check_scenario_data(self, scenario_folder, scenario):
        HAS_SCENARIO = False
        HAS_TEXT = False
        HAS_IMAGE = False
        HAS_RDF = False
        print(scenario_folder)
        for f in os.listdir(scenario_folder):
            if f==scenario+'.json':
                HAS_SCENARIO=True
            if (scenario+'.json').endswith(f):
                HAS_SCENARIO=True
            elif f=='text.json':
                HAS_TEXT=True
            elif f=='image.json':
                HAS_IMAGE=True
            elif f=='rdf':
                HAS_RDF=True
        return HAS_SCENARIO, HAS_TEXT, HAS_IMAGE, HAS_RDF


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

    def get_utterance_stats(self, utterances):
        total_utt_length = 0
        total_token_length = 0
        total_tokens = 0
        for utt in utterances:
            tokens = utt[1].split(" ")
            total_utt_length += len(utt[1])
            total_tokens += len(tokens)
            for token in tokens:
                total_token_length += len(token)

        average_token_length = total_token_length/ total_tokens
        average_tokens_per_utt = total_tokens/len(utterances)
        average_utt_length = total_utt_length/len(utterances)
        return average_utt_length, average_tokens_per_utt, average_token_length

    def get_overview_statistics(self,scenario_folder):
        stat_dict = {}

        storage = ScenarioStorage(scenario_folder)
        scenarios = list(storage.list_scenarios())
        print("Processing scenarios: ", scenarios)
        columns = ["Label"]

        for scenario in scenarios:
            columns.append(scenario)
            csv_path = os.path.join(scenario_folder, scenario, "evaluation", scenario+"_meta_data.csv")
            if not os.path.exists(csv_path):
                print("No evaluation file for:", csv_path)
                continue

            file = open(csv_path, 'r')

            print('Reading file for overview', file.name)
            lines = [x.strip() for x in file.readlines()]
            anno_type = "General"
            scenario_dict = {}
            if anno_type in stat_dict:
                scenario_dict = stat_dict.get(anno_type)
            nr = 0
            for fields in lines:
                nr+=1
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
                    print('Error in line', nr, ' nr. of fields:', len(fields), fields)
                    continue
        return stat_dict, columns

    def get_overview_statistics_any_depth(self, folder):
        stat_dict = {}
        columns = ["Label"]

        for f in glob.glob(folder+"/**/*_meta_data.json", recursive=True):
            scenario_dir = os.path.dirname(os.path.dirname(f))
            speaker = None
            file = open(f, 'r')
            print(file.name)
            meta = json.load(file)
            scenario = meta['Scenario']['Scenario_id']
            columns.append(scenario)

            anno_type="Scenario"
            scenario_info = meta[anno_type]
            if anno_type in stat_dict:
                scenario_dict = stat_dict.get(anno_type)
            else:
                scenario_dict = {}
            for key, value in scenario_info.items():
                if key=="Speaker":
                    speaker = value
                if key in scenario_dict:
                    scenario_dict[key].append((scenario, value))
                else:
                    scenario_dict[key] = [(scenario, value)]
            stat_dict[anno_type] = scenario_dict

            anno_type = "Text"
            scenario_info = meta[anno_type]
            if anno_type in stat_dict:
                scenario_dict = stat_dict.get(anno_type)
            else:
                scenario_dict = {}
            for key, value in scenario_info.items():
                if key=="Text_annotations":
                    for akey, avalue in scenario_info[key].items():
                        if akey in scenario_dict:
                            scenario_dict[akey].append((scenario, avalue))
                        else:
                            scenario_dict[akey] = [(scenario, avalue)]
                else:
                    if key in scenario_dict:
                        scenario_dict[key].append((scenario, value))
                    else:
                        scenario_dict[key] = [(scenario, value)]
            stat_dict[anno_type] = scenario_dict

            anno_type = "Image"
            scenario_info = meta[anno_type]
            if anno_type in stat_dict:
                scenario_dict = stat_dict.get(anno_type)
            else:
                scenario_dict = {}
            for key, value in scenario_info.items():
                if key=="Image_annotations":
                    for akey, avalue in scenario_info[key].items():
                        if akey in scenario_dict:
                            scenario_dict[akey].append((scenario, avalue))
                        else:
                            scenario_dict[akey] = [(scenario, avalue)]
                else:
                    if key in scenario_dict:
                        scenario_dict[key].append((scenario, value))
                    else:
                        scenario_dict[key] = [(scenario, value)]
            stat_dict[anno_type] = scenario_dict
            try:
                if speaker:
                    basename = os.path.basename(scenario_dir)
                    scenario_dir_new = os.path.join(folder,speaker+"_"+basename)
                    if not os.path.exists(scenario_dir_new):
                        os.mkdir(scenario_dir_new)
                    os.rename(scenario_dir, scenario_dir_new)
            except:
                print(scenario_dir_new)
        return stat_dict, columns

    def save_overview_globally(self, folder, stat_dict, columns):
        dfall = pd.DataFrame(columns=columns)
        for key in stat_dict.keys():
            # dfall.update
            anno_dict = stat_dict.get(key)
            sorted_keys = list(anno_dict.keys())
            sorted_keys.sort()
            for anno in sorted_keys:
                values = anno_dict.get(anno)
                row = {'Label': anno}
                for value in values:
                    scenario = value[0]
                    count = value[1]
                    row.update({scenario: count})
                dfall = dfall.append(row, ignore_index=True)
            ##dfall.to_csv(os.path.join(folder, key + ".csv"))
        dfall.to_csv(os.path.join(folder, "overview" + ".csv"))
            # print(dfall.info())

    def save_overview_statistics(self, scenario_folder, stat_dict, columns):
        utterance_row = {'Label':'Utterances'}
        image_row = {'Label':'Images'}
        storage = ScenarioStorage(scenario_folder)
        scenarios = list(storage.list_scenarios())
        for scenario in scenarios:
            scenario_ctrl = storage.load_scenario(scenario)
            text_signals = scenario_ctrl.get_signals(Modality.TEXT)
            image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
            utterance_row.update({scenario: len(text_signals)})
            image_row.update({scenario: len(image_signals)})

        for key in stat_dict.keys():
            dfall = pd.DataFrame(columns=columns)
            dfall = dfall.append(utterance_row, ignore_index=True)
            dfall = dfall.append(image_row, ignore_index=True)
            anno_dict = stat_dict.get(key)
            ### adding the nr of turns to the stats

            for anno in anno_dict.keys():
                values = anno_dict.get(anno)
                row = {'Label': anno}
                for value in values:
                    scenario = value[0]
                    count = value[1]
                    row.update({scenario: count})
                dfall = dfall.append(row, ignore_index=True)
            file_path = os.path.join(scenario_folder, key+".csv")
            print("Saving overview to:", file_path)
            dfall.to_csv(file_path)


    def analyse_interaction(self, emissor_folder, scenario_id, metrics_to_plot=None):
        scenario_folder = os.path.join(emissor_folder, scenario_id)
        # Save
        evaluation_folder = os.path.join(scenario_folder, 'evaluation')
        if not os.path.exists(evaluation_folder):
            os.mkdir(evaluation_folder)
        meta = ""
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        print("scenario_folder", scenario_folder)
        scenario_storage = ScenarioStorage(emissor_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        meta+='SCENARIO_FOLDER\t'+ scenario_folder+"\n"
        meta+='SCENARIO_ID\t'+ scenario_id+"\n"
        speaker = "No speaker"
        try:
            speaker = scenario_ctrl.scenario.context.speaker["name"] if "name" in scenario_ctrl.scenario.context.speaker else "No speaker"
        except:
            print("No speaker in context")
        agent = "No agent"
        try:
            agent = scenario_ctrl.scenario.context.agent["name"] if "name" in scenario_ctrl.scenario.context.agent else "No agent"
        except:
            print("No speaker in context")
        location = "No location"
        try:
            location = scenario_ctrl.scenario.context.location_id  #### Change this to location name when this implemented
        except:
            print("No location id in context")
        meta+='AGENT\t'+agent+'\n'
        meta+='SPEAKER\t'+speaker+'\n'
        meta+='LOCATION\t'+location+'\n'

        people = "Not in context"
        try:
            people = scenario_ctrl.scenario.context.persons
        except:
            print("No location id in context")
        objects = "Not in context"
        try:
            objects = scenario_ctrl.scenario.context.objects
        except:
            print("No location id in context")

        meta+='PEOPLE SEEN\t'+str(people)+'\n'
        meta+='OBJECTS SEEN\t'+str(objects)+'\n'
        duration = self.get_duration_in_minutes(scenario_ctrl)
        meta+='DURATION IN MINUTES\t'+str(duration)+"\n"

        #### Text signals statistics
        meta+="\nText signals\n"
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        plot.create_timeline_image(scenario_path=scenario_folder, scenario=scenario_id, speaker=speaker, agent=agent,
                              signals=text_signals)

        ids, turns, speakers = text_util.get_utterances_with_context_from_signals(text_signals)
        meta+='NR. TURNS\t'+ str(len(turns))+"\n"
        average_turn_length, average_tokens_per_turn, average_token_length = self.get_utterance_stats(turns)
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
        file_path = os.path.join(evaluation_folder, file_name)
        with open(file_path, 'w') as f:
            f.write(meta)

        # Get likelihood scored
        # speaker_turns = {k: [] for k in speakers}
        #df = self._calculate_metrics(turns, speaker_turns)

        #@TODO make a nicer table
        #df = pd.DataFrame(text_temp_rows)

        #self._save(df, evaluation_folder, scenario_id)


    def analyse_interaction_json(self, emissor_folder, scenario_id, metrics_to_plot=None):
        scenario_folder = os.path.join(emissor_folder, scenario_id)
        # Save
        evaluation_folder = os.path.join(scenario_folder, 'evaluation')
        if not os.path.exists(evaluation_folder):
            os.mkdir(evaluation_folder)
        meta = {}
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        print("scenario_folder", scenario_folder)
        scenario_storage = ScenarioStorage(emissor_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        t = {}
        #t['SCENARIO_FOLDER'] = scenario_folder
        t['Scenario_id']= scenario_id
        speaker = scenario_ctrl.scenario.context.speaker["name"]
        agent = scenario_ctrl.scenario.context.agent["name"]
        location = scenario_ctrl.scenario.context.location_id  #### Change this to location name when this implemented
        t['Agent']=agent
        t['Speaker']=speaker
        t['Location']=location

        people = scenario_ctrl.scenario.context.persons
        objects = scenario_ctrl.scenario.context.objects
        t['People_seen '] = str(people)
        t['Objects_seen']= str(objects)
        duration = self.get_duration_in_minutes(scenario_ctrl)
        t['Duration_in_minutes'] = str(duration)
        meta["Scenario"]=t

        #### Text signals statistics
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        ids, utterances, speakers = text_util.get_utterances_with_context_from_signals(text_signals)
        t = {}
        t['Nr.utterances'] = str(len(utterances))
        average_utt_length, average_tokens_per_utt, average_token_length = self.get_utterance_stats(utterances)
        t['Average_utterance_length'] = str(average_utt_length)
        t['Average_tokens_per_utterance'] = str(average_tokens_per_utt)
        t['Average_token_length'] = str(average_token_length)

        text_type_counts, text_type_timelines, nr_annotations = self.get_statistics_from_signals(text_signals)
       # rows.extend(self.get_statistics_from_image_annotation(scenario_ctrl, scenario_id))

        t['Nr.annotations']=  str(nr_annotations)
        items = {}
        for key in text_type_counts.keys():
            counts = text_type_counts.get(key)
            for c in counts:
                items[c]=str(counts.get(c))

        t['Text_annotations']=items
        meta["Text"]=t


        t={}
        image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
        t["Nr.images"]=str (len(image_signals))
        text_type_counts, text_type_timelines, nr_annotations = self.get_statistics_from_signals(image_signals)
        t[ 'Nr.annotations']=  str(nr_annotations)
        items = {}
        for key in text_type_counts.keys():
            counts = text_type_counts.get(key)
            for c in counts:
                items[c] = str(counts.get(c))
        t['Image_annotations'] = items
        meta["Image"]=t

            # testing
        print(meta)

        ## Save the meta data
        file_name = scenario_id + "_meta_data.json"
        file_path = os.path.join(evaluation_folder, file_name)
        with open(file_path, 'w') as f:
            json_object = json.dumps(meta, indent=4)
            f.write(json_object)


    def _get_annotation_dict (self, signals:[Signal]):
            all_annotations = []
            type_dict = {}
            for signal in signals:
                mentions = signal.mentions
                timestamp = signal.time.start
                for mention in mentions:
                    annotations = mention.annotations
                    all_annotations.append((timestamp, annotations))
            for pair in all_annotations:
                time_key = pair[0]
                anno = pair[1]
                if anno:
                    type_key = anno[0].type
                    value = anno[0].value
                    if not type_key=='Face' and not type_key==None:
                        #### create a dict with all values for each annotation type
                        if not type_dict.get(type_key):
                            type_dict[type_key] = [(time_key, value)]
                        else:
                            type_dict[type_key].append((time_key, value))
            return type_dict, len(all_annotations)

    def _get_get_value_from_annotation(self, annotation):
        anno = ""
        if isinstance(annotation, str):
            anno = "faceID:"+annotation
        else:
            try:
                # value is the correct python object
                value_dict = vars(annotation)
                anno = "label:" + value_dict
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
                    else:
                        print('UNKNOWN annotation', annotation)
                    anno = type+":"+value
                except:
                    if annotation:
                        print('UNKNOWN annotation type', type(annotation), annotation)

        return anno

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
        plt.xticks(ax.get_xticks()[::5], rotation=45)

        plot_file = evaluation_folder / f"{xlabel}.png"
        g.figure.savefig(plot_file, dpi=300, transparent=True, bbox_inches='tight')
        plt.close()
        print(f"\tSaved to file: {plot_file}")

    def _save(self, df, evaluation_folder, scenario_id):
        file_name =  scenario_id+"_statistical_analysis.csv"
        df.to_csv(evaluation_folder / file_name, index=False)


#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='GO', confidence=0.7935183048248291, value='anger'),
#Annotation(type='python-type:cltl.dialogue_act_classification.api.DialogueAct', value=JSON(type='MIDAS', confidence=3.6899490356445312, value='opinion'),
#Annotation(type='ConversationalAgent', value='SPEAKER', source='LEOLANI', timestamp=1665746858876)
#Annotation(type='python-type:cltl.emotion_extraction.api.Emotion', value=JSON(type='SENTIMENT', confidence=0.9314287331653759, value='negative'), source='python-source:cltl.emotion_extraction.utterance_go_emotion_extractor', timestamp=1665746860001)
