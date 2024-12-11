from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import cltl.dialogue_evaluation.utils.scenario_check as check
import os
import argparse
import sys


def process_all_scenarios(emissor_path:str, scenarios:[]):
    evaluator = StatisticalEvaluator()
    # for scenario in scenarios:
    #         if not scenario.startswith("."):
    #             scenario_path = os.path.join(emissor_path, scenario)
    #             has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
    #             check_message = "Scenario:" + scenario + "\n"
    #             check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
    #             check_message += "\tText JSON:" + str(has_text) + "\n"
    #             check_message += "\tImage JSON:" + str(has_image) + "\n"
    #             check_message += "\tRDF :" + str(has_rdf) + "\n"
    #             print(check_message)
    #             if not has_scenario:
    #                 print("No scenario JSON found. Skipping:", scenario_path)
    #             elif not has_text:
    #                 print("No text JSON found. Skipping:", scenario_path)
    #             else:
    #                 evaluator.analyse_interaction(emissor_path, scenario)
    stats_dict, columns = evaluator.get_overview_statistics_any_depth(emissor_path)
    print(columns)
    if stats_dict:
        evaluator.save_overview_globally(emissor_path, stats_dict, columns)
    else:
        print("No stats for:", emissor_path)

def main(emissor_path:str, scenario:str):
    folders = []
    if os.path.exists(emissor_path):
        if not scenario:
            folders = os.listdir(emissor_path)
        else:
            folders = [scenario]

        ### For testing
    emissor_path = "/Users/piek/Desktop/d-Leolani/leolani-mmai-parent/cltl-leolani-app/py-app/storage/emissor"
    folders = ["e3e655bc-8c19-4fe6-9481-18c8c6f3d1cb", "c441c977-f46a-4847-b035-93252c2d7367","f85d7821-0b56-4261-ac46-55582d05b7d9", "5f412ab2-1ad5-4bee-889d-976bcf255f94"]
    process_all_scenarios(emissor_path, folders)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor-path', type=str, required=False, help="Path to the emissor folder", default='emissor')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)

    main(args.emissor_path, args.scenario)

