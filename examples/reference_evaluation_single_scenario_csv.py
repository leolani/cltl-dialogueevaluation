import json
import pandas as pd
from cltl.dialogue_evaluation.reference_evaluation import ReferenceEvaluator
from pathlib import Path
import os

evaluator = ReferenceEvaluator()
METRIC = ["blue", "rouge", "bertscore", "meteor"]
#nlg_metrics =['rouge','blue','sacrebleu','bleurt', 'meteor','google_bleu', 'harshhpareek/bertscore', 'all']

def make_overview_json(submission_path):
    overviewdf= pd.DataFrame()
    for f in os.listdir(submission_path):
        if f.endswith(".json"):
            print(f)
            file_path = os.path.join(submission_path, f)
            result = json.load(open(file_path))
            overviewrow= {'File': result['File'],
                          'System utterances' : result['System utterances'],
                          'References': result['Reference utterances']}
            for score in result['Scores']:
                if score['metric']=='blue':
                    overviewrow.update({'blue_precision': score['precisions'], 'blue_brevity' : score['brevity_penalty']})
                elif score['metric']=='rouge':
                    overviewrow.update({'rouge1': score['rouge1'], 'rouge2' :score['rouge2'], 'rougeL' :score['rougeL']})

                elif score['metric']=='bertscore':
                    overviewrow.update({'bert_precision': score['precision'], 'bert_recall' :score['recall'], 'bert_f1' :score['f1']})

                elif score['metric']=='meteor':
                    overviewrow.update({'meteor': score['meteor']})
            #for manual in result['manual']:
            if 'manual' in result:
                overviewrow.update(result['manual'])


            print(overviewrow)
            overviewdf = overviewdf.append(overviewrow, ignore_index=True)
    file = os.path.join(submission_path, "overview-reference-manual.csv")
    overviewdf.to_csv(file)


submission_path = "/Users/piek/Desktop/t-MA-Combots-2023/assignments/evaluation/emissor"
#submission_path = "/Users/piek/Desktop/t-MA-Combots-2023/assignments/test"

for f in os.listdir(submission_path):
    #if f=='Angus_liud_133551_7051251_Angus_manual_evaluation.xlsx':
    if f.endswith(".xlsx"):
        print(f)
        file_path = os.path.join(submission_path, f)
        eval_file_path = os.path.join(submission_path, f+".json")
        result = evaluator.evaluate_conversation_single_scenario_csv(csv_name = f, csv_file=file_path, metrics_to_plot=METRIC)
        json_object = json.dumps(result, indent=4)
        with open(eval_file_path, "w") as outfile:
            outfile.write(json_object)


make_overview_json(submission_path)