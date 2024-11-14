from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os

def main():
    evaluator = StatisticalEvaluator()
    emissor_path = '../examples/data/emissor'
    scenario = "2fe112e2-31cf-4aef-9011-d237135e53fb"
    scenario = "3cf7c0b8-f69d-45e8-b804-cb6aca3a044d"
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



if __name__ == '__main__':
    main()
