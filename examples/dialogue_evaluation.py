import pandas as pd

import cltl.dialogue_evaluation.utils.text_signal as text_util
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
from cltl.dialogue_evaluation.metrics.utterance_likelihood import USR_MLM

def main ():
    scenario_path = "/Users/piek/Desktop/d-Leolani/leolani-mmai-parent/cltl-leolani-app/py-app/storage/emissor"
    ### The name of your scenario
    scenario_id = "ff3bf631-2086-497d-8b71-67627165e2a9" ##### Blenderbot - Leolani
    print('scenario_path:', scenario_path)
    max_context=300
    ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
    scenarioStorage = ScenarioStorage(scenario_path)
    scenario_ctrl = scenarioStorage.load_scenario(scenario_id)
    signals = scenario_ctrl.get_signals(Modality.TEXT)
    turns, speakers = text_util.get_turns_with_context_from_signals(signals, max_context)
    print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)
    print('Speakers:', speakers)
    print('Max context:', max_context)

    ###### GET LIKELIHOOD SCORES
    top = 20  ### this defines the number results returned by the LM for a masked token that we compare against
    model_path_mlm = 'adamlin/usr-topicalchat-roberta_ft'
    model_mlm = USR_MLM(path=model_path_mlm, top_results=top)

    speaker_mlm_scores = {k: [] for k in speakers}
    speaker_mlm_max_scores = {k: [] for k in speakers}
    speaker_turns = {k: [] for k in speakers}

    turn_index = []
    rows = []
    previous_speaker = None
    for index, turn in enumerate(turns):
        turn_index.append(index)
        context = turn[0]
        target = turn[1]
        cue = turn[2]
        speaker = turn[3]
        llh, best_sentence, max_score = model_mlm.sentence_likelihood(context, target)
        row = {"Turn": index, "Speaker": speaker, "Cue": cue, "Response": target, "Context": context,
               "MLM response": best_sentence, "System llh": llh, "MLM llh": max_score}
        rows.append(row)

        if speaker:
            speaker_turns[speaker].append(index)
            speaker_mlm_scores[speaker].append(llh)
            speaker_mlm_max_scores[speaker].append(max_score)

    annotation_columns = ["Overall Human Rating", "Interesting", "Engaging", "Specific", "Relevant", "Correct",
                          "Semantically Appropriate", "Understandable", "Fluent"]
    

    result_frame = pd.DataFrame(rows)
    for annotation in annotation_columns:
        result_frame[annotation]=""
    result_frame.head()

    file = scenario_id + "_turns" + str(len(turns)) + "_context" + str(max_context) + ".csv"
    result_frame.to_csv(file, index=False)

    overall_rows = []
    for speaker in speakers:
        turns = speaker_turns[speaker]
        mlm_scores = speaker_mlm_scores[speaker]
        mlm_max_scores = speaker_mlm_max_scores[speaker]

        mlm_average_score = sum(mlm_scores) / len(mlm_scores)
        mlm_average_max_score = sum(mlm_max_scores) / len(mlm_max_scores)
        overall_rows.append(
            {'Speaker': speaker, 'Nr. turns': len(turns), 'MLM': mlm_average_score, 'MLM max': mlm_average_score})

    overall_result_frame = pd.DataFrame(overall_rows)
    overall_result_frame.head()

    file = scenario_id + "_turns" + str(len(turns)) + "_context" + str(max_context) + "_overall.csv"
    overall_result_frame.to_csv(file, index=False)
    
    


if __name__ == '__main__':
    main()
