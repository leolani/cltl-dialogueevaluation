from cltl.dialogue_evaluation.statistical_evaluation import StatisticalEvaluator
import os
evaluator = StatisticalEvaluator()
import cltl.dialogue_evaluation.utils.scenario_check as check

def student_submissions (submission_path):
    for path in os.listdir(submission_path):
        student_path = os.path.join(submission_path, path)
        if os.path.isdir(student_path):
          print(student_path)
          for scenario in os.listdir(student_path):
              scenario_path = os.path.join(student_path, scenario)
              if os.path.isdir(scenario_path):
                  has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
                  check_message = "Scenario folder:" + scenario_path + "\n"
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
                        evaluator.analyse_interaction_json(student_path, scenario)


def server_submission(submission_path):
      for scenario in os.listdir(submission_path):
          scenario_path = os.path.join(submission_path, scenario)
          if os.path.isdir(scenario_path):
              has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
              check_message = "Scenario folder:" + scenario_path + "\n"
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
                    evaluator.analyse_interaction_json(submission_path, scenario)

def aggregate_results(submission_path):
    stats_dict, columns = evaluator.get_overview_statistics_any_depth(submission_path)
    print(columns)
    if stats_dict:
        evaluator.save_overview_globally(submission_path, stats_dict, columns)
    else:
        print("No stats for:", submission_path)


if __name__ == "__main__":
    submission_path="/Users/piek/Desktop/t-MA-Combots-2024/assignments/assignment-1/"
   # submission_path="/Users/piek/Desktop/t-MA-Combots-2024/assignments/assignment-1/leolani_local/emissor"
   # submission_path="/Users/piek/Desktop/t-MA-Combots-2024/assignments/assignment-1/leolani_text_to_ekg_restrained/emissor"
   # submission_path="/Users/piek/Desktop/t-MA-Combots-2024/assignments/assignment-1/leolani_text_to_ekg_wild/emissor"
    aggregate_results(submission_path)
