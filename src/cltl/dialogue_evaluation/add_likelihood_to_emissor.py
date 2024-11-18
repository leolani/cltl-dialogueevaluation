import logging
from typing import Iterable
import uuid
from dataclasses import dataclass
from cltl.dialogue_evaluation.metrics.utterance_likelihood import USR_MLM

from cltl.combot.event.emissor import AnnotationEvent
from cltl.combot.infra.time_util import timestamp_now
from emissor.representation.scenario import Mention, TextSignal, Annotation, class_type
from emissor.persistence import ScenarioStorage
from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator
import cltl.dialogue_evaluation.utils.scenario_check as check
from emissor.persistence.persistence import ScenarioController
from emissor.processing.api import SignalProcessor
from emissor.representation.scenario import Modality, Signal
logger = logging.getLogger(__name__)

@dataclass

class Likelihood:
    score: float
    model: str
    max: float


@dataclass
class LikelihoodEvent(AnnotationEvent[Annotation[Likelihood]]):
    @classmethod
    def create_text_mention(cls, text_signal: TextSignal, llh: Likelihood , source: str):
        return cls(class_type(cls), [LikelihoodEvent.to_mention(text_signal, llh, source)])

    @staticmethod
    def to_mention(text_signal: TextSignal, llh: Likelihood, source: str) -> Mention:
        """
        Create Mention with annotations.
        """
        segment = text_signal.ruler
        annotation = Annotation("Likelihood", llh, source, timestamp_now())

        return Mention(str(uuid.uuid4()), [segment], [annotation])

class LikelihoodAnnotator (SignalProcessor):

    def __init__(self, model: str, model_name: str, max_content: int, top_results: int):
        """ an evaluator that will use reference metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        self._classifier = USR_MLM(path=model, top_results=top_results)
            #LikelihoodEvaluator(model=model, max_context=max_content, len_top_tokens=top_tokens)
        self._model_name = model_name
        self._max_context = max_content
        self._max_text_length=514
        self._context = ""


    def process_signal(self, scenario: ScenarioController, signal: Signal):
        if not signal.modality == Modality.TEXT:
            return
        mention = self.annotate(signal)
        signal.mentions.append(mention)

    def annotate(self, textSignal):
        utterance = textSignal.text
        if len(utterance)> self._max_text_length:
            utterance=utterance[:self._max_text_length]
        likelihood, expected_target, max_likelihood = self._classifier.sentence_likelihood(self._context, utterance)
        mention = LikelihoodEvent.to_mention(textSignal, likelihood, self._model_name)
        ### Update the context
        self._context += utterance
        if len(self._context)> self._max_context:
            self._context=self._context[:self._max_context]

        return mention


if __name__ == "__main__":

    model_path = "/Users/piek/Desktop/d-Leolani/resources/models/usr-topicalchat-roberta_ft"
    model_path = "google-bert/bert-base-multilingual-cased"
    annotator = LikelihoodAnnotator(model=model_path, model_name="USR", max_content=300, top_results=20)
    scenario_folder = "/Users/piek/Desktop/d-Leolani/tutorials/test10/leolani-text-to-ekg/app/py-app/storage/emissor"
    scenario_folder = "/Users/piek/Desktop/t-MA-Combots-2024/code/ma-communicative-robots/emissor_chat/emissor"
    scenario_folder = "/Users/piek/Desktop/t-MA-Combots-2024/code/ma-communicative-robots/leolani_text_to_ekg/storage/emissor"
    scenario_storage = ScenarioStorage(scenario_folder)
    scenarios = list(scenario_storage.list_scenarios())
    print("Processing scenarios: ", scenarios)
    for scenario in scenarios:
        print('Processing scenario', scenario)
        scenario_ctrl = scenario_storage.load_scenario(scenario)
        signals = scenario_ctrl.get_signals(Modality.TEXT)
        for signal in signals:
            annotator.process_signal(scenario=scenario_ctrl, signal=signal)
        #### Save the modified scenario to emissor
        scenario_storage.save_scenario(scenario_ctrl)

