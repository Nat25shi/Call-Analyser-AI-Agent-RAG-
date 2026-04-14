# Call-Analyser-AI-Agent-RAG-
​This project implements an intelligent Call Analyser Agent that uses Retrieval-Augmented Generation (RAG) and Deterministic Tool Routing to analyze customer call transcripts. The agent can summarize specific interactions, list unresolved issues, and provide sentiment analysis based on call outcomes.
​1. My Approach
​The architecture is designed to prioritize data groundedness over creative AI generation. I followed a four-step pipeline:
​A. Task 1: Semantic Indexing (RAG)
​I used the all-MiniLM-L6-v2 Sentence Transformer model to convert customer complaints into vector embeddings. This allows the bot to understand the "meaning" behind a user's question, rather than just matching keywords.
​B. Task 2:  LLM Connectivity
​I integrated Google Gemini 2.5-flash-lite. Unlike a standard chatbot, this agent is "grounded." I pass the specific row from the CSV as "Context" into the prompt, forcing the AI to answer only based on the provided data.
​C. Task 3: Deterministic Tooling
​For high accuracy data like "Resolution Status" or "Sentiment," I built two dedicated Python methods:
​get_call_outcome(): Directly queries the CSV for the 'Outcome' column.
​get_sentiment_summary(): Uses internal logic to map 'Unresolved' or 'Escalated' statuses to a 'Negative' sentiment label.
​This prevents the AI from "hallucinating" or guessing a status incorrectly.
​D. Task 4: The Routing Agent
​The core "brain" of the script is the ask method. It uses Regex to detect Call IDs and routes the query to the correct logic:
​Direct ID Match (Critical Fix): If a user mentions CALL_003, the agent bypasses vector search and pulls that exact row. This fixed the issue where the bot previously mixed up similar-sounding calls.
​Global Reasoning: For summary requests, the agent filters the DataFrame for all "Unresolved" rows and passes the entire batch to the LLM to summarize

Example Outputs
​Test 1: 
​User: What happened in CALL_003? Bot: The customer inquired about EMI options for a laptop purchase using a debit card. The agent clarified that EMI is only available on select credit cards and suggested checking the mobile app for further details.
​Test 2:
​User: Give me a summary of unresolved calls. Bot: The unresolved issues primarily involve technical errors with transactions (CALL_008), delays in refund processing (CALL_011), and persistent product defects, such as a faulty mixer grinder (CALL_016). Most customers are frustrated with the lack of immediate solutions.
​Test 3:
​User: What was the sentiment in CALL_005? Bot: Sentiment is Negative (Reason: status is escalated).
​4. Constraint Handling
​Encoding: Handled latin-1 encoding for CSV compatibility.
Security: API keys are managed via python-dotnev to keep credentials out of source code
​Security: API keys are managed via python-dotenv to keep credentials out of the source code.
