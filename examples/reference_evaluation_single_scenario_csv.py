import json
import pandas as pd
from cltl.dialogue_evaluation.reference_evaluation import ReferenceEvaluator
from pathlib import Path
import os

evaluator = ReferenceEvaluator()
METRIC = ["blue", "rouge", "bertscore", "meteor"]
#nlg_metrics =['rouge','blue','sacrebleu','bleurt', 'meteor','google_bleu', 'harshhpareek/bertscore', 'all']

# evaluate.list_evaluation_modules = ['precision', 'code_eval', 'roc_auc', 'cuad', 'xnli', 'rouge', 'pearsonr', 'mse', 'super_glue', 'comet', 'cer', 'sacrebleu', 'mahalanobis',
#            'wer', 'competition_math', 'f1', 'recall', 'coval', 'mauve', 'xtreme_s', 'bleurt', 'ter', 'accuracy', 'exact_match', 'indic_glue', 'spearmanr',
#            'mae', 'squad', 'chrf', 'glue', 'perplexity', 'mean_iou', 'squad_v2', 'meteor', 'bleu', 'wiki_split', 'sari', 'frugalscore',
#            'google_bleu', 'bertscore', 'matthews_correlation', 'seqeval', 'trec_eval', 'rl_reliability', 'angelina-wang/directional_bias_amplification',
#            'cpllab/syntaxgym', 'kaggle/ai4code', 'codeparrot/apps_metric', 'mfumanelli/geometric_mean', 'poseval', 'brier_score', 'abidlabs/mean_iou',
#            'abidlabs/mean_iou2', 'giulio98/codebleu', 'mase', 'mape', 'smape', 'dvitel/codebleu', 'NCSOFT/harim_plus', 'JP-SystemsX/nDCG', 'Drunper/metrica_tesi',
#            'jpxkqx/peak_signal_to_noise_ratio', 'jpxkqx/signal_to_reconstruction_error', 'hpi-dhc/FairEval', 'nist_mt', 'lvwerra/accuracy_score', 'character',
#            'charcut_mt', 'ybelkada/cocoevaluate', 'harshhpareek/bertscore', 'posicube/mean_reciprocal_rank', 'bstrai/classification_report',
#            'omidf/squad_precision_recall', 'Josh98/nl2bash_m', 'BucketHeadP65/confusion_matrix', 'BucketHeadP65/roc_curve', 'yonting/average_precision_score',
#            'transZ/test_parascore', 'transZ/sbert_cosine', 'hynky/sklearn_proxy', 'unnati/kendall_tau_distance', 'r_squared', 'Viona/fuzzy_reordering',
#            'Viona/kendall_tau', 'lhy/hamming_loss', 'lhy/ranking_loss', 'Muennighoff/code_eval_octopack', 'yuyijiong/quad_match_score',
#            'Splend1dchan/cosine_similarity', 'AlhitawiMohammed22/CER_Hu-Evaluation-Metrics', 'Yeshwant123/mcc', 'transformersegmentation/segmentation_scores',
#            'sma2023/wil', 'chanelcolgate/average_precision', 'ckb/unigram', 'Felipehonorato/eer', 'manueldeprada/beer', 'tialaeMceryu/unigram',
#            'He-Xingwei/sari_metric', 'langdonholmes/cohen_weighted_kappa', 'fschlatt/ner_eval', 'hyperml/balanced_accuracy', 'brian920128/doc_retrieve_metrics',
#            'guydav/restrictedpython_code_eval', 'k4black/codebleu', 'Natooz/ece', 'ingyu/klue_mrc', 'Vipitis/shadermatch', 'unitxt/metric',
#            'gabeorlanski/bc_eval', 'jjkim0807/code_eval', 'mcnemar', 'exact_match', 'wilcoxon', 'kaleidophon/almost_stochastic_order', 'word_length',
#            'lvwerra/element_count', 'word_count', 'text_duplicates', 'perplexity', 'label_distribution', 'toxicity', 'regard', 'honest', 'ybelkada/toxicity',
#            'ronaldahmed/ccl_win', 'meg/perplexity', 'cakiki/tokens_per_byte', 'lsy641/distinct']



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