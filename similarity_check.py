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
                print("Error: No models found in LM Studio.")
                sys.exit(1)
        except Exception as e:
            print(f"Error fetching models from LM Studio: {e}")
            sys.exit(1)

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
        print(f"Error getting embedding from LM Studio (Model: {model_name}): {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Detailed Prompt Similarity Detector")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--prompt", help="Prompt text to check (required if --file not used)")
    parser.add_argument("--file", help="Path to a file containing the prompt (alternative to --prompt)")
    parser.add_argument("--url", default=LM_STUDIO_DEFAULT_URL, help="LM Studio API Base URL")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold (0.0 to 1.0)")
    parser.add_argument("--model", help="Specific model name to use for embeddings")
    
    args = parser.parse_args()
    args.project = args.project.lower()

    # Handle prompt input source
    if args.file:
        try:
            with open(args.file, 'r') as f:
                args.prompt = f.read().strip()
            if not args.prompt:
                print(f"Error: File '{args.file}' is empty.")
                sys.exit(1)
        except Exception as e:
            print(f"Error reading prompt from file '{args.file}': {e}")
            sys.exit(1)
    elif not args.prompt:
        print("Error: Either --prompt or --file must be provided.")
        parser.print_help()
        sys.exit(1)

    # 1. Connect to DB
    try:
        db = DBManager()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    # 2. Get embedding for the new prompt
    print(f"Generating embedding for prompt in project '{args.project}'...")
    embedding = get_embedding(args.prompt, args.url, args.model)
    
    # 3. Check for similarity
    print("Checking for similar prompts in database...")
    similar_prompts = db.find_similar(args.project, embedding, threshold=args.threshold)

    if similar_prompts:
        print("\n[!] WARNING: Similar or duplicate prompts found:")
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
                        print(f"Error: ID {pid} not found in the similar list.")
                except ValueError:
                    print("Error: Please enter a valid numerical ID.")
            elif choice == 's':
                break
            elif choice == 'n':
                print("Prompt not saved.")
                db.close()
                return
    else:
        print("\n[+] No similar prompts found.")

    # 4. Save to database
    print("Saving prompt to database...")
    try:
        # Check if vector size matches
        # The DBManager ensures schema, but we might need to handle dimension mismatch
        db.save_prompt(args.project, args.prompt, embedding)
        print("[+] Prompt saved successfully.")
    except Exception as e:
        if "different dimensions" in str(e):
            print(f"Error: Embedding dimension mismatch. The database expected a different size.")
            print("You might need to recreate the table with the correct dimension.")
        else:
            print(f"Error saving prompt: {e}")

    db.close()

if __name__ == "__main__":
    main()
