from pathlib import Path
import os
from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator
from cltl.dialogue_evaluation.usr_dialogue_retrieval_evaluation import USR_DialogRetrieval_Evaluator
import cltl.dialogue_evaluation.utils.scenario_check as check

SUBMISSION_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction-robot/emissor")

def apply_usr_to_conversation_csv (input_folder, mlm, ctx, uk):
    SCENARIOS = sorted([path for path in input_folder.iterdir()
                        if path.is_dir() and path.stem not in ['.idea', 'plots']])

    for SCENARIO_FOLDER in SCENARIOS:
        print(SCENARIO_FOLDER)
        print(SCENARIO_FOLDER.stem)
        has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(SCENARIO_FOLDER, SCENARIO_FOLDER.stem)
        check_message = "Scenario folder:" + str(SCENARIO_FOLDER) + "\n"
        check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
        check_message += "\tText JSON:" + str(has_text) + "\n"
        check_message += "\tImage JSON:" + str(has_image) + "\n"
        check_message += "\tRDF :" + str(has_rdf) + "\n"
        print(check_message)
        if not has_scenario:
            print("No scenario JSON file found. Aborting.")
        elif not has_text:
            print("No text JSON file found. Aborting.")
        else:
            if mlm:
                # ft = basic model fine-tuned with conversational data
                mlm.evaluate_conversation(scenario_folder=input_folder, scenario_id=SCENARIO_FOLDER.stem)
            if ctx:
                # ctx = uses context only
                ctx.evaluate_conversation(scenario_folder=input_folder, scenario_id=SCENARIO_FOLDER.stem)
            if uk:
                #uk = uses knowledge & context
                uk.evaluate_conversation(scenario_folder=input_folder, scenario_id=SCENARIO_FOLDER.stem)




if __name__ == "__main__":
    submission_path = '/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction-offline'
    #submission_path = '/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction-online'
    #submission_path = '/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction-robot/emissor'
    evaluator_ctx = None
    evaluator_uk = None
    evaluator_mlm = None

    #ft = basic model fine-tuned with conversational data
    #evaluator = LikelihoodEvaluator(model_path_mlm='adamlin/usr-topicalchat-roberta_ft', max_context=300, len_top_tokens=20)
    evaluator_mlm = LikelihoodEvaluator(model_path_mlm='/Users/piek/Desktop/d-Leolani/resources/models/usr-topicalchat-roberta_ft', max_context=300, len_top_tokens=20)
    # ctx = uses context only
    #evaluator = USR_DialogRetrieval_Evaluator(model_path_ctx='adamlin/usr-topicalchat-ctx', context_type="ctx", max_context=300, len_top_tokens=20)
    #evaluator_ctx = USR_DialogRetrieval_Evaluator(model_path_ctx='/Users/piek/Desktop/d-Leolani/resources/models/usr-topicalchat-ctx', context_type="ctx", max_context=300, len_top_tokens=20)

    #uk = uses knowledge & context
    #evaluator = USR_DialogRetrieval_Evaluator(model_path_ctx='adamlin/usr-topicalchat-uk', context_type="fct", max_context=300, len_top_tokens=20)
    #evaluator_uk = USR_DialogRetrieval_Evaluator(model_path_ctx='/Users/piek/Desktop/d-Leolani/resources/models/usr-topicalchat-uk', context_type="fct", max_context=300, len_top_tokens=20)

    for persona in os.listdir(submission_path):
        persona_folder = os.path.join(submission_path, persona)
        if os.path.isdir(persona_folder):
            print(persona_folder)
            apply_usr_to_conversation_csv(Path(persona_folder), evaluator_mlm, evaluator_ctx, evaluator_uk)
