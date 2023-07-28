import os
import json
from pathlib import Path
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
import evaluate
import cltl.dialogue_evaluation.utils.text_signal as text_util
from cltl.dialogue_evaluation.api import BasicEvaluator

#https://github.com/huggingface/evaluate
#https://huggingface.co/spaces/evaluate-metric/bleu

class ReferenceEvaluator(BasicEvaluator):
    def __init__(self):
        """Creates an evaluator that will use reference metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        super(ReferenceEvaluator, self).__init__()
        self._log.debug(f"Reference Evaluator ready")

    def evaluate_conversation(self, ref_scenario_folder,
                              sys_scenario_folder,
                              ref_scenario_id,
                              sys_scenario_id, metrics_to_plot=None):
        # Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        ref_scenario_storage = ScenarioStorage(ref_scenario_folder)
        ref_scenario_ctrl = ref_scenario_storage.load_scenario(ref_scenario_id)
        ref_signals = ref_scenario_ctrl.get_signals(Modality.TEXT)
        ref_ids, ref_turns, ref_speakers = text_util.get_turns_with_context_from_signals(ref_signals, max_context=0)

        print('Reference SCENARIO_FOLDER:', ref_scenario_folder)
        print('Nr of reference turns:', len(ref_turns), ' extracted from reference scenario: ', ref_scenario_id)
        print('Reference Speakers:', ref_speakers)

        sys_scenario_storage = ScenarioStorage(sys_scenario_folder)
        sys_scenario_ctrl = sys_scenario_storage.load_scenario(sys_scenario_id)
        sys_signals = sys_scenario_ctrl.get_signals(Modality.TEXT)
        sys_ids, sys_turns, sys_speakers = text_util.get_turns_with_context_from_signals(sys_signals, max_context=0)


        print('System SCENARIO_FOLDER:', sys_scenario_folder)
        print('Nr of system turns:', len(sys_turns), ' extracted from reference scenario: ', sys_scenario_id)
        print('system Speakers:', sys_speakers)
        references = text_util.get_uterances_from_turns(sys_turns)
        predictions = text_util.get_uterances_from_turns(ref_turns)

        bleu = evaluate.load("bleu")
        results = bleu.compute(predictions=predictions, references=references)
        print(results)
        #
        # # Save
        evaluation_folder_path = os.path.join(sys_scenario_folder, sys_scenario_id, 'evaluation')
        ##evaluation_folder = os.path.(evaluation_folder_path)
        if not os.path.exists(evaluation_folder_path):
            os.mkdir(evaluation_folder_path)
        self._save(results, evaluation_folder_path)
        # #
#        if metrics_to_plot:
#             self.plot_metrics_progression(metrics_to_plot, [df], evaluation_folder)

    @staticmethod
    def _calculate_metrics(model_mlm, turns, speaker_mlm_scores, speaker_mlm_max_scores, speaker_turns):
        # Iterate turns
        print(f"\n\tCalculating likelihood scores")
        rows = []
        for index, turn in enumerate(turns):
            print(f"\t\tProcessing turn {index}/{len(turns)}")
            context = turn[0]
            target = turn[1]
            cue = turn[2]
            speaker = turn[3]
            llh, best_sentence, max_score = model_mlm.sentence_likelihood(context, target)
            rows.append({"Turn": index, "Speaker": speaker, "Cue": cue, "Response": target, "Context": context,
                         "MLM response": best_sentence, "System llh": llh, "MLM llh": max_score})

            if speaker:
                speaker_turns[speaker].append(index)
                speaker_mlm_scores[speaker].append(llh)
                speaker_mlm_max_scores[speaker].append(max_score)

        return pd.DataFrame(rows)

    def _save(self, results, evaluation_folder):
        file_path = os.path.join(evaluation_folder, "reference_evaluation.csv")
        file = open(file_path, "w")
        json.dump(results, file, indent=4)

