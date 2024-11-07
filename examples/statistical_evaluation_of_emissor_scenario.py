from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os



def main():
    evaluator = StatisticalEvaluator()
    emissor_path = '/Users/piek/Desktop/t-MA-Combots-2024/code/ma-communicative-robots/emissor_chat/emissor'
    scenario = "261c370e-eaea-479f-ac41-cbfd7de227ac"

    #emissor_path ="/Users/piek/Desktop/t-MA-Combots-2024/code/ma-communicative-robots/leolani_text_to_ekg/storage/emissor"
    #scenario = "9e589730-4485-4412-b8b1-701eecf87607"
    scenario_path = os.path.join(emissor_path, scenario)
    has_scenario, has_text, has_image, has_rdf = evaluator.check_scenario_data(scenario_path, scenario)
    check_message = "Scenario folder:" + emissor_path + "\n"
    check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
    check_message += "\tText JSON:" + str(has_text) + "\n"
    check_message += "\tImage JSON:" + str(has_image) + "\n"
    check_message += "\tRDF :" + str(has_rdf) + "\n"
    print(check_message)
    if not has_scenario:
        print("No scenario JSON found. Skipping:", scenario_path)
    elif not has_text:
        print("No text JSON found. Skipping:", scenario_path)
    else:
        evaluator.analyse_interaction(emissor_path, scenario)

    # stats_dict, columns = evaluator.get_overview_statistics(emissor_path)
    # evaluator.save_overview_statistics(emissor_path, stats_dict, columns)


if __name__ == '__main__':
    main()
#
# for scenario in os.listdir(emissor_path):
#     if not scenario.startswith("."):
#         scenario_path = os.path.abspath(scenario)
#         print('Path', scenario_path)
#         print('Scenario', scenario)
#         has_scenario, has_text, has_image, has_rdf = evaluator.check_scenario_data(scenario_path, scenario)
#         check_message = "Scenario folder:" + scenario_path + "\n"
#         check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
#         check_message += "\tText JSON:" + str(has_text) + "\n"
#         check_message += "\tImage JSON:" + str(has_image) + "\n"
#         check_message += "\tRDF :" + str(has_rdf) + "\n"
#         print(check_message)
#         if not has_scenario:
#             print("No scenario JSON found. Skipping:", scenario_path)
#         elif not has_text:
#             print("No text JSON found. Skipping:", scenario_path)
#         else:
#             evaluator.analyse_interaction_json(scenario_path, scenario)