from pathlib import Path
import os
import pandas as pd
from cltl.dialogue_evaluation.likelihood_evaluation import LikelihoodEvaluator
from cltl.dialogue_evaluation.usr_dialogue_retrieval_evaluation import USR_DialogRetrieval_Evaluator
import cltl.dialogue_evaluation.utils.scenario_check as check

SUBMISSION_FOLDER = Path("/Users/piek/Desktop/t-MA-Combots-2023/assignments/interaction-robot/emissor")

def apply_usr_to_conversation_csv (input_folder, mlm, ctx, uk):
    SCENARIOS = sorted([path for path in Path(input_folder).iterdir()
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


def make_overview_csv(submission_path):
    overviewdf= pd.DataFrame()
    for persona in os.listdir(submission_path):
        persona_folder = os.path.join(submission_path, persona)
        if os.path.isdir(persona_folder):
            print(persona_folder)
            SCENARIOS = sorted([path for path in Path(persona_folder).iterdir()
                                if path.is_dir() and path.stem not in ['.idea', 'plots']])
            for SCENARIO_FOLDER in SCENARIOS:
                print(SCENARIO_FOLDER)
                likelihood_result_csv = os.path.join(SCENARIO_FOLDER, "evaluation", "likelihood_evaluation_context300_overall.csv")
                if os.path.exists(likelihood_result_csv):
                    overviewrow = {"persona" : persona, "scenario" : SCENARIO_FOLDER.stem}
                    df = pd.read_csv(likelihood_result_csv)
                    for index, row in df.iterrows():
                        if row['Speaker']=='speaker':
                            overviewrow.update({"Turns" : row['Nr. turns']})
                            overviewrow.update({"Speaker_MLM_LLH" : row['MLM avg']})
                            overviewrow.update({"Speaker_MLM_max": row['MLM avg max']})
                        elif row['Speaker']=='LEOLANI':
                            #overviewrow.update({"Leolani_turns" : row['Nr. turns']})
                            overviewrow.update({"Leolani_MLM_LLH" : row['MLM avg']})
                            overviewrow.update({"Leolani_MLM_max" : row['MLM avg max']})
                    print(overviewrow)
                    overviewdf = overviewdf.append(overviewrow, ignore_index=True)
    file = os.path.join(submission_path, "overview-mlm.csv")
    overviewdf.to_csv(file)

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
            apply_usr_to_conversation_csv(persona_folder, evaluator_mlm, evaluator_ctx, evaluator_uk)

    make_overview_csv(submission_path)