import re
from langchain_ollama import ChatOllama
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
import cltl.dialogue_evaluation.utils.text_signal as text_util
#import cltl.dialogue_evaluation.utils.image_signal as image_util
from emissor.representation.scenario import Signal

from cltl.dialogue_evaluation.api import BasicEvaluator

def get_judge_prompt():
    instruction = """
                    ### Role Assignment
                    You are a Coherence Evaluation Judge.
                    Your job is to evaluate how coherent the **assistant’s response** is with respect to the **user’s input**.
                    
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

if __name__ == "__main__":
    # Example usage
    test_messages = [
        {"role": "user", "content": "What do you think about hotels in Paris?"},
        {"role": "assistant", "content": "I like to go to London. It's a nice city."}
    ]
    print("Testing coherence evaluation:")
    model = "qwen3:1.7b"
    model = "qwen3:0.6b"
    ollama_client = get_chat_model(model_name=model)
    evaluation = query_qwen_as_a_judge_ollama(test_messages, ollama_client)
    print(f"Coherence Score: {evaluation['coherence_score']}")
    print(f"Explanation: {evaluation['explanation']}")
