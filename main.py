import time
from router import classify_intent, route_and_respond, log_request

def main():
    test_messages = [
        "how do i sort a list of objects in python?",
        "explain this sql query for me",
        "This paragraph sounds awkward, can you help me fix it?",
        "I'm preparing for a job interview, any tips?",
        "what's the average of these numbers: 12, 45, 23, 67, 34",
        "Help me make this better.",
        "I need to write a function that takes a user id and returns their profile, but also i need help with my resume.",
        "hey",
        "Can you write me a poem about clouds?", # Should be 'unclear'
        "Rewrite this sentence to be more professional.",
        "I'm not sure what to do with my career.",
        "what is a pivot table",
        "fxi thsi bug pls: for i in range(10) print(i)",
        "How do I structure a cover letter?",
        "My boss says my writing is too verbose."
    ]

    print("Starting LLM Prompt Router evaluation...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"[{i}/{len(test_messages)}] User: {message}")
        
        # Step 1: Classify Intent
        intent_dict = classify_intent(message)
        intent = intent_dict.get("intent", "unclear")
        confidence = intent_dict.get("confidence", 0.0)
        
        print(f"   -> Classification: Intent='{intent}', Confidence={confidence}")
        
        # Step 2: Route and Respond
        final_response = route_and_respond(message, intent_dict)
        preview = final_response[:100].replace("\n", " ") + "..." if len(final_response) > 100 else final_response.replace("\n", " ")
        print(f"   -> Response Preview: {preview}\n")
        
        # Step 3: Log Request
        log_request(
            intent=intent,
            confidence=confidence,
            user_message=message,
            final_response=final_response
        )
        
        # Rest slightly between requests to respect basic rate limits
        time.sleep(1)
        
    print("Evaluation complete! Results logged to route_log.jsonl")

if __name__ == "__main__":
    main()
