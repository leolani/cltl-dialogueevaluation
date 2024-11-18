import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
from emissor.representation.scenario import Signal
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
import cltl.dialogue_evaluation.utils.text_signal as text_signal_util

_THRESHOLD = 0.6
_ANNOTATIONS =["go", "sentiment"] #["sentiment", "ekman"]
# Mock data for a conversation
data = {
    'Turn': [1, 2, 3, 4, 5, 6],
    'Speaker': ['A', 'B', 'A', 'B', 'A', 'B'],
    'Dialogue Act': ['Greeting', 'Question', 'Answer', 'Statement', 'Request', 'Confirmation'],
    'Emotion': ['Happy', 'Curious', 'Neutral', 'Satisfied', 'Hopeful', 'Affirmative']
}

def get_signal_rows(signals:[Signal], human, agent, annotations:[]):
    data = []
    # row = {'turn': 0, 'utterance': "", 'score': 3, "speaker": agent, "type": "",
    #        "annotation": ""}
    # data.append(row)
    for i, signal in enumerate(signals):
        speaker = text_signal_util.get_speaker_from_text_signal(signal)
        if speaker=='SPEAKER':
            speaker = human
        else:
            speaker = agent
        text = ''.join(signal.seq)
        score = 0
        score += text_signal_util.get_dact_feedback_score_from_text_signal(signal)
        if "sentiment" in annotations:
            score += text_signal_util.get_sentiment_score_from_text_signal(signal)
        if "ekman" in annotations:
            score += text_signal_util.get_ekman_feedback_score_from_text_signal(signal)
        if "go" in annotations:
            score += text_signal_util.get_go_feedback_score_from_text_signal(signal)
        label = text_signal_util.make_annotation_label(signal, _THRESHOLD, _ANNOTATIONS)
        row = {'turn':i+1, 'utterance': text, 'score': score, "speaker": speaker, "type":signal.modality, "annotation": label}
        data.append(row)
    return data


def create_timeline_image(scenario_path, scenario, speaker:str, agent:str, signals:[Signal]):
   # earliest, latest, period, activity_in_period = get_activity_in_period(story_of_life, current_date=current_date)

    rows = get_signal_rows(signals, speaker, agent, _ANNOTATIONS)
    plt.rcParams['figure.figsize'] = [len(rows), 5]
    df = pd.DataFrame(rows)
    #print(df.head())
    sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
    ax = sns.lineplot(x='turn', y='score', data=df, hue='speaker', style='annotation', markers=True, palette="bright", legend="brief")
    #palette = "flare/bright/deep/muted/colorblind/dark"
    for index, row in df.iterrows():
        x = row['turn']
        y = row['score']
        category = row['speaker']+":"+str(row['utterance'])
        category += '\n'+str(row['annotation'])
        ax.text(x, y,
                s=" " + str(category),
                rotation=70,
                horizontalalignment='left', size='x-small', color='black', verticalalignment='bottom',
                linespacing=1.5)

    ax.tick_params(axis='x', rotation=70)
    # Save the plot
    plt.legend(loc='lower right')
    plt.ylim(-3,3)
    path =  os.path.join(scenario_path, scenario+"_plot.png")
    plt.savefig(path, dpi=600)
    plt.show()



def main():
    emissor_path = '/Users/piek/Desktop/d-Leolani/tutorials/test22/cltl-text-to-ekg-app/app/py-app/storage/emissor'
    emissor_path ="/Users/piek/Desktop/t-MA-Combots-2024/code/ma-communicative-robots/leolani_text_to_ekg/storage/emissor"
    scenario ="d5a6bc60-c19b-4c08-aee5-b4dd1c65c64d"
    scenario_path = os.path.join(emissor_path, scenario)
    print(scenario_path)
    scenario_storage = ScenarioStorage(emissor_path)
    scenario_ctrl = scenario_storage.load_scenario(scenario)
    speaker = scenario_ctrl.scenario.context.speaker["name"]
    agent = scenario_ctrl.scenario.context.agent["name"]
    text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    create_timeline_image(scenario_path=scenario_path, scenario=scenario, speaker=speaker, agent=agent, signals=text_signals)

if __name__ == '__main__':
    main()
