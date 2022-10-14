from pathlib import Path

import pandas as pd
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality

import cltl.dialogue_evaluation.utils.text_signal as text_util
from cltl.dialogue_evaluation.api import BasicEvaluator


class StatisticalEvaluator(BasicEvaluator):
    def __init__(self):
        """Creates an evaluator that will calculate basic statistics for evaluation
        params
        returns: None
        """
        super(StatisticalEvaluator, self).__init__()

        self._log.debug(f"Statistical Evaluator ready")

    def evaluate_conversation(self, scenario_folder, scenario_id, metrics_to_plot=None):
        ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        scenario_storage = ScenarioStorage(scenario_folder)
        scenario_ctrl = scenario_storage.load_scenario(scenario_id)
        # TODO: fix next line, it's broken
        signals = scenario_ctrl.get_signals(Modality.TEXT)
        turns, speakers = text_util.get_turns_with_context_from_signals(signals)

        print('SCENARIO_FOLDER:', scenario_folder)
        print('Nr of turns:', len(turns), ' extracted from scenario: ', scenario_id)
        print('Speakers:', speakers)

        # Get likelihood scored
        speaker_turns = {k: [] for k in speakers}

        df = self._calculate_metrics(turns, speaker_turns)

        # Save
        evaluation_folder = Path(scenario_folder + '/' + scenario_id + '/evaluation/')
        evaluation_folder.mkdir(parents=True, exist_ok=True)
        self._save(df, evaluation_folder)

    @staticmethod
    def _calculate_metrics(turns, speaker_turns):
        # Iterate turns
        rows = []
        for index, turn in enumerate(turns):
            # TODO count things here (e.g. entities mentioned,
            pass

        return pd.DataFrame(rows)

    def _save(self, df, evaluation_folder):
        df.to_csv(evaluation_folder / "statistical_evaluation.csv", index=False)
