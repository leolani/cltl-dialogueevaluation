import sys

import cltl.dialogue_evaluation.utils.text_signal as text_util

from cltl.dialogue_evaluation.metrics.utterance_likelihood import USR_MLM
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, TextSignal, Mention, Annotation, Scenario
import getopt

#  THIS SCRIPT USES A REIMPLEMENTATION OF THE USR METRICS FOR EVALUATING DIALOGUES. THE BASICS ARE DESCRIBED IN THE FOLLOWING PAPER:
# Mehri, Shikib, and Maxine Eskenazi. "Usr: An unsupervised and reference free evaluation metric for dialog generation." arXiv preprint arXiv:2005.00456 (2020).
# https://arxiv.org/pdf/2005.00456.pdf
#
# OUR IMPLEMENTATION USES THE MODELS PROVIDED BY THE AUTHORS: http://shikib.com/usr AND ALSO AVAILABLE ON HUGGINGFACE.COM
# WE REIMPLEMENTED THE LML SCORE USING A MASKED LIKELIHOOD FOR THE TARGET SENTENCE.
# THIS SCRIPT LOADS A DIALIGUE FROM THE EMISSOR DATA FORMAT. THE DETAILS OF THE EMISSOR FORMAT ARE EXPLAINED HERE: https://github.com/cltl/EMISSOR
#
# YOU CAN CREATE EMISSOR DIALOGUES USING THE CHATBOT NOTEBOOKS AND SCRIPTS IN THIS REPOSITORY
#

if __name__ == "__main__":

    metric=None
    top=20
    scenario_path=None
    scenario_id=None
    max_context=200

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:t:p:s:c:", ["metric=", "scenario-path=", "scenario-name", "top-result", "max-context"])
    except getopt.GetoptError:
        print('Usage:', 'evaluate_emissor_dialogue -p <scenario-path> -s  <scenario_name> -m <metric> -c <max-context>')
        print('Metric values:\n\tMLM= Likelikehood by Masked Language Model', '\n\tALL= all three scores')
        sys.exit(2)
    if len(sys.argv)==1:
        print('Usage:', 'evaluate_emissor_dialogue -p <scenario-path> -s  <scenario_name> -m <metric> -c <max-context>')
        print('Metric values:\n\tMLM= Likelikehood by Masked Language Model', '\n\tALL= all three scores')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print('Usage:', 'evaluate_emissor_dialogue -p <scenario-path> -s  <scenario_name> -m <metric>')
            print('Metric values:\n\tMLM= Likelikehood by Masked Language Model', '\n\tALL= all three scores')
            sys.exit()
        elif opt in ("-p", "--scenario-path"):
            print('Scenario-path:', arg)
            scenario_path = arg
        elif opt in ("-s", "--scenario-name"):
            print('Scenario-name:', arg)
            scenario_id = arg
        elif opt in ("-m", "--metric"):
            print('USR metric:', arg)
            metric = arg
        elif opt in ("-t", "--top-result"):
            print('Top-result:', arg)
            top = int(arg)
        elif opt in ("-c", "--max-context"):
            print('Max-context:', arg)
            max_context = int(arg)

    ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
    scenarioStorage = ScenarioStorage(scenario_path)
    scenario_ctrl = scenarioStorage.load_scenario(scenario_id)
    signals = scenario_ctrl.get_signals(Modality.TEXT)

    turns, speakers = text_util.get_turns_with_context_from_signals(signals, max_context)
    print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)


    print('Metric:', "MLM")

    speaker_mlm_scores = {k: [] for k in speakers}
    speaker_mlm_max_scores = {k: [] for k in speakers}
    speaker_turns = {k: [] for k in speakers}

    model_path_mlm = 'adamlin/usr-topicalchat-roberta_ft'
    model_mlm = USR_MLM(path=model_path_mlm, top_results=top)
    for index, turn in enumerate(turns):
        context = turn[0]
        target = turn[1]
        cue=turn[2]
        speaker = turn[3]
        llh, best_sentence, max_score = model_mlm.sentence_likelihood(context,target)
        print('Turn:', index)
        print('Speaker:', speaker)
        print('Input:', cue)
        print('Response', target)
        print('\tLikelihood:', llh)
        print('Best model response', best_sentence)
        print('\tMax score:', max_score)

        if speaker:
            speaker_turns[speaker].append(index)
            speaker_mlm_scores[speaker].append(llh)
            speaker_mlm_max_scores[speaker].append(max_score)

    for speaker in speakers:
        scores = speaker_mlm_scores[speaker]
        average_score = sum(scores) / len(scores)

        max_scores = speaker_mlm_max_scores[speaker]
        average_max_score = sum(max_scores) / len(max_scores)
        print('\nSpeaker:', speaker, ' # turns:', len(speaker_turns[speaker]))
        print('Average score:', average_score)
        print('Sequence profile:', scores)
        print('Average max score:', average_max_score)
        print('Sequence max profile:', max_scores)


