import argparse
import requests
import json
import sys
from db_manager import DBManager

LM_STUDIO_DEFAULT_URL = "http://localhost:1234/v1"

def get_embedding(prompt, base_url, model_name=None):
    if not model_name:
        # Try to find an embedding model
        try:
            models_resp = requests.get(f"{base_url}/models")
            models_resp.raise_for_status()
            models = models_resp.json().get('data', [])
            # Prefer models with 'embed' in the name
            embedding_models = [m['id'] for m in models if 'embed' in m['id'].lower()]
            if embedding_models:
                model_name = embedding_models[0]
            elif models:
                model_name = models[0]['id']
            else:
                raise RuntimeError("No models found in LM Studio.")
        except Exception as e:
            raise RuntimeError(f"Error fetching models from LM Studio: {e}")

    url = f"{base_url}/embeddings"
    payload = {
        "input": prompt,
        "model": model_name
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['embedding']
    except Exception as e:
        raise RuntimeError(f"Error getting embedding from LM Studio (Model: {model_name}): {e}")

def analyze_requirements(prompt, requirements, base_url, model_name=None):
    if not requirements or requirements.strip() == "":
        return None
    
    if not model_name:
        # For simplicity, we'll try to use the same model as embedding OR a chat model
        # But usually you need a chat/instruct model for analysis. 
        # LM Studio often lists chat models in /models too.
        try:
            models_resp = requests.get(f"{base_url}/models")
            models = models_resp.json().get('data', [])
            chat_models = [m['id'] for m in models if 'embed' not in m['id'].lower()]
            if chat_models:
                model_name = chat_models[0]
            else:
                model_name = models[0]['id']
        except:
            return "Internal Error: Could not fetch models for requirement analysis."

    url = f"{base_url}/chat/completions"
    system_prompt = (
        "You are a Quality Assurance assistant. Your task is to compare a user's prompt against a set of project requirements. "
        "Identify any conflicts or missing elements. If there are no issues, respond with 'NO ISSUES'. "
        "If there are issues, list them clearly and concisely."
    )
    user_message = f"PROJECT REQUIREMENTS:\n{requirements}\n\nUSER PROMPT TO CHECK:\n{prompt}\n\nDoes the prompt meet all requirements? If not, why?"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            error_body = response.text
            if "context length" in error_body.lower() or "tokens to keep" in error_body.lower():
                return (
                    "Requirement analysis error: Context limit exceeded. \n"
                    "Tip: Increase 'Context Length (n_ctx)' in LM Studio settings (e.g., to 8192 or 16384) "
                    "or use a high-context model like 'Phi-3-mini-128k-instruct'."
                )
            return f"Requirement analysis error: {response.status_code} - {error_body}"
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"Requirement analysis error (Exception): {e}"

def main():
    parser = argparse.ArgumentParser(description="Detailed Prompt Similarity Detector")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--environment", required=True, help="Environment name")
    parser.add_argument("--file", required=True, help="Path to a file containing the prompt")
    parser.add_argument("--url", default=LM_STUDIO_DEFAULT_URL, help="LM Studio API Base URL")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold (0.0 to 1.0)")
    parser.add_argument("--model", help="Specific model name to use (embeddings and analysis)")
    
    args = parser.parse_args()

    # 1. Read prompt from file
    try:
        with open(args.file, 'r') as f:
            prompt_text = f.read().strip()
        if not prompt_text:
            print(f"Error: File '{args.file}' is empty.")
            sys.exit(1)
    except Exception as e:
        print(f"Error reading prompt from file '{args.file}': {e}")
        sys.exit(1)

    # 2. Connect to DB and fetch Environment/Project
    try:
        db = DBManager()
        env_data = db.get_environment_by_name(args.project, args.environment)
        if not env_data:
            print(f"Error: Environment '{args.environment}' for project '{args.project}' not found.")
            print("Please create them first using manage_project.py and manage_environment.py.")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to database or fetching data: {e}")
        sys.exit(1)

    # 3. Requirement Analysis
    print(f"\n[~] Analyzing prompt against requirements for project '{args.project}'...")
    req_analysis = analyze_requirements(prompt_text, env_data['requirements'], args.url, args.model)
    if req_analysis:
        if "NO ISSUES" not in req_analysis.upper():
            print("\n[!] REQUIREMENT ISSUES DETECTED:")
            print("-" * 30)
            print(req_analysis)
            print("-" * 30)
            while True:
                cont = input("\nDo you want to continue with similarity check anyway? (y/n): ").lower()
                if cont == 'n':
                    print("Aborted by user.")
                    db.close()
                    return
                elif cont == 'y':
                    break
        else:
            print("[+] Prompt meets all project requirements.")
    else:
        print("[i] No requirements defined for this project.")

    # 4. Get embedding
    print(f"\n[~] Generating embedding for prompt...")
    embedding = get_embedding(prompt_text, args.url, args.model)
    
    # 5. Check for similarity
    print(f"[~] Checking for similar prompts in environment '{args.environment}'...")
    similar_prompts = db.find_similar(env_data['id'], embedding, threshold=args.threshold)

    if similar_prompts:
        print("\n[!] WARNING: Similar prompts found in this environment:")
        similar_map = {p['id']: p for p in similar_prompts}
        
        for p in similar_prompts:
            print(f"--- Similarity: {p['similarity']:.4f} ---")
            print(f"ID: {p['id']}")
            print(f"Text: {p['prompt_text'][:200]}...")
            print("-" * 30)
        
        while True:
            choice = input("\nOptions: (v) View full prompt by ID, (s) Save anyway, (n) Don't save: ").lower()
            if choice == 'v':
                try:
                    pid = int(input("Enter ID to view: "))
                    if pid in similar_map:
                        print("\n" + "="*50)
                        print(f"FULL TEXT FOR ID {pid}:")
                        print("-" * 50)
                        print(similar_map[pid]['prompt_text'])
                        print("="*50 + "\n")
                    else:
                        print(f"Error: ID {pid} not found.")
                except ValueError:
                    print("Error: Invalid ID.")
            elif choice == 's':
                break
            elif choice == 'n':
                print("Prompt not saved.")
                db.close()
                return
    else:
        print("[+] No similar prompts found in this environment.")

    # 6. Save to database
    print("\n[~] Saving prompt to database...")
    try:
        db.save_prompt(env_data['id'], prompt_text, embedding)
        print("[+] Prompt saved successfully.")
    except Exception as e:
        print(f"Error saving prompt: {e}")

    db.close()

if __name__ == "__main__":
    main()
