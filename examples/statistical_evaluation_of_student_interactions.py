from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os
evaluator = StatisticalEvaluator()
import cltl.dialogue_evaluation.utils.scenario_check as check

submissions_path='/Users/piek/Desktop/t-MA-Combots-2023/assignments/interactions/submissions-1'

# for path in os.listdir(submissions_path):
#     student_path = os.path.join(submissions_path, path)
#     if os.path.isdir(student_path):
#       print(student_path)
#       for scenario in os.listdir(student_path):
#           scenario_path = os.path.join(student_path, scenario)
#           if os.path.isdir(scenario_path):
#               has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
#               check_message = "Scenario folder:" + scenario_path + "\n"
#               check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
#               check_message += "\tText JSON:" + str(has_text) + "\n"
#               check_message += "\tImage JSON:" + str(has_image) + "\n"
#               check_message += "\tRDF :" + str(has_rdf) + "\n"
#               print(check_message)
#               if not has_scenario:
#                   print("No scenario JSON file found. Aborting.")
#               elif not has_text:
#                   print("No text JSON file found. Aborting.")
#               else:
#                     evaluator.analyse_interaction_json(student_path, scenario)



stats_dict, columns = evaluator.get_overview_statistics_any_depth(submissions_path)
print(columns)
if stats_dict:
    evaluator.save_overview_globally(submissions_path, stats_dict, columns)
else:
    print("No stats for:", submissions_path)