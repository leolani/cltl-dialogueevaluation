import re
import os
from ollama import Client
from langchain_ollama import ChatOllama
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
from emissor.representation.scenario import TextSignal

def get_judge_prompt():
    instruction = """
                    ### Role Assignment
                    You are a Coherence Evaluation Judge.
                    Your job is to evaluate how coherent the **assistant’s response** is with respect to the **user’s input**.
                    The **assistant’s response** may be a follow up question to a statement from the **user** or a related statement itself.

                    ### Task Definition
                    You must:
                    1. Assign a **coherence score** from **0.0 to 1.0**
                    2. Provide a **short explanation** (maximum 2 sentences)

                    ### Output Format (STRICT)
                    Return ONLY:

                    <JSON>
                    {
                      "coherence_score": float between 0.0 and 1.0,
                      "explanation": "brief rationale"
                    }
                    </JSON>
                    """

    system_prompt = {
        "role": "system",
        "content": instruction
    }
    return system_prompt


def query_qwen_as_a_judge_ollama_cloud(messages, ollama_client, model):
    system_prompt = get_judge_prompt()
    messages_judge = [system_prompt] + messages
    response = ""
    for part in ollama_client.chat(model=model, messages=messages_judge, stream=True, format="json"):
        response += part['message']['content']
    # Look for patterns like "coherence_score": 0.9 or similar
    #     </analysis<|message|>The user said: "Lucy drinks wine". The assistant gave a garbled nonsense response. That's incoherent. Score low, maybe 0.0 or 0.1. Provide explanation.{
    #   "coherence_score": 0.0,
    #   "explanation": "The assistant's output is nonsensical and does not address the simple statement about Lucy drinking wine."
    #    }
    try:
        score_pattern = r'"coherence_score":\s*([\d.]+)'
        explanation_pattern = r'"explanation":\s*"([^"]+)"'

        score_match = re.search(score_pattern, response)
        explanation_match = re.search(explanation_pattern, response)

        if score_match and explanation_match:
            coherence_score = float(score_match.group(1))
            explanation = explanation_match.group(1)
            return {"coherence_score": coherence_score, "explanation": explanation}
        else:
            return {"coherence_score": None, "explanation": "Could not extract score and explanation from response"}
    except Exception as e:
        return {"coherence_score": None, "explanation": f"Error processing response: {str(e)}"}

def get_chat_model(model_name="qwen3:0.6b"):
    return ChatOllama(model=model_name,
                      format="json",
                      temperature=0.0,
                      max_tokens=2000,
                      top_p=0.95,
                      top_k=40,
                      think=False)

def query_qwen_as_a_judge_ollama(messages, ollama_client):
    system_prompt = get_judge_prompt()
    messages_judge = [system_prompt] + messages
    response = ollama_client.invoke(messages_judge)
    print(response.content)

    try:
        # Look for patterns like "coherence_score": 0.9 or similar
        score_pattern = r'"coherence_score":\s*([\d.]+)'
        explanation_pattern = r'"explanation":\s*"([^"]+)"'

        score_match = re.search(score_pattern, response.content)
        explanation_match = re.search(explanation_pattern, response.content)

        if score_match and explanation_match:
            coherence_score = float(score_match.group(1))
            explanation = explanation_match.group(1)
            return {"coherence_score": coherence_score, "explanation": explanation}
        else:
            return {"coherence_score": None, "explanation": "Could not extract score and explanation from response"}
    except Exception as e:
        return {"coherence_score": None, "explanation": f"Error processing response: {str(e)}"}

def get_text_signals_from_a_scenario(emissor_folder: str, scenario_id: str):
    text_signals = []
    scenario_folder = os.path.join(emissor_folder, scenario_id)
    scenario_storage = ScenarioStorage(emissor_folder)
    scenario_ctrl = scenario_storage.load_scenario(scenario_id)
    try:
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    except:
        print('Error loading text signals from text.json')
    return text_signals

def get_speaker_from_text_signal(textSignal: TextSignal):
    speaker = None
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'ConversationalAgent':
                speaker = annotation.value
                break
        if speaker:
            break
    return speaker


if __name__ == "__main__":
    # Example usage
    test_messages = [
        {"role": "user", "content": "What do you think about hotels in Paris?"},
        {"role": "assistant", "content": "I like to go to London. It's a nice city."}
    ]
    print("Testing coherence evaluation:")
#    model = "qwen3:1.7b"
#    model = "qwen3:0.6b"
 #   ollama_client = get_chat_model(model_name=model)

    # evaluation = query_qwen_as_a_judge_ollama(test_messages, ollama_client)
    # print(f"Coherence Score: {evaluation['coherence_score']}")
    # print(f"Explanation: {evaluation['explanation']}")
    # OpenAI API Key
    path = "../../ollama-cloud-key.txt"
    api_key = "THIS SHOULD BE YOUR OLLAMA CLOUD API KEY"
    with open(path) as f:
        api_key = f.read()

    ollama_client = Client(host="https://ollama.com", headers={'Authorization': 'Bearer ' + api_key})
    EMISSOR = "./data/emissor"
    SCENARIO = "14a1c27d-dfd2-465b-9ab2-90e9ea91d214"

    text_signals = get_text_signals_from_a_scenario(EMISSOR, SCENARIO)
    conversation = []
    for text_signal in text_signals:
        signal_speaker = get_speaker_from_text_signal(text_signal)  # SPEAKER or agent
        if signal_speaker == "SPEAKER":
            turn = {"role": "user", "content": text_signal.text}
        else:
            turn = {"role": "assistant", "content": text_signal.text}
        conversation.append(turn)
    model = "gpt-oss:120b"

    coherence_scores = []
    for turn in conversation[:8]:
        print(turn)
        if turn["role"] == "user":
            pair = [turn]
        else:
            pair.append(turn)
            coherence = query_qwen_as_a_judge_ollama(pair, ollama_client, model)
            print(coherence)
            if "coherence_score" in coherence:
                coherence_scores.append(coherence["coherence_score"])

    average_coherence = sum(coherence_scores) / len(coherence_scores)
    print("Average coherence", average_coherence)
    print(coherence_scores)

