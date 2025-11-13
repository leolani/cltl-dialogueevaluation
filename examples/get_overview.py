from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import pandas as pd
import os
import cltl.dialogue_evaluation.utils.scenario_check as check


def check_all_scenarios(emissor_path:str, scenarios:[]):
    evaluator = StatisticalEvaluator()
    for scenario in scenarios:
            if not scenario.startswith("."):
                scenario_path = os.path.join(emissor_path, scenario)
                has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
                check_message = "Scenario:" + scenario + "\n"
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
                    evaluator.analyse_interaction_json(emissor_path, scenario)
    stats_dict, columns = evaluator.get_overview_statistics_any_depth(emissor_path)
    print(columns)
    if stats_dict:
        evaluator.save_overview_globally(emissor_path, stats_dict, columns)
    else:
        print("No stats for:", emissor_path)

def main():
    # Example path to EMISSOR data
    emissor_path = "./data/emissor"
    emissor_path = "/Users/piek/Desktop/t-MA-Combots-2025/code/ma-communicative-robots/evaluate/data/emissor"

    # Get list of scenarios from the emissor path
    try:
        scenarios = [f for f in os.listdir(emissor_path) if os.path.isdir(os.path.join(emissor_path, f))]
        print('The scenarios are:', scenarios)
        # Run the check for all scenarios
        check_all_scenarios(emissor_path, scenarios)

    except FileNotFoundError:
        print(f"Error: The path '{emissor_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()