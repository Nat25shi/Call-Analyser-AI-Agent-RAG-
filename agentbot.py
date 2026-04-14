import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_ai = genai.GenerativeModel("gemini-2.5-flash-lite")

print("Loading AI models...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

class CallAgent:
    def __init__(self, csv_path):
        # Load the CSV data
        try:
            self.df = pd.read_csv(csv_path, encoding='latin-1')
        except FileNotFoundError:
            print(f"Error: The file '{csv_path}' was not found.")
            self.df = pd.DataFrame() 
            return
        
        self.df = self.df.astype(str)
        
        # Prepare data 
        self.info_list = []
        for index, row in self.df.iterrows():
            combined = row['Call ID'] + " " + row['Customer Complaint / Query']
            self.info_list.append(combined)
            
        self.vectors = embed_model.encode(self.info_list)
        print("Bot is ready!")

    # Tool 1 Status
    def get_call_outcome(self, call_id):
        row = self.df[self.df['Call ID'] == call_id]
        if not row.empty:
            status = row['Outcome'].values[0]
            return f"Tool 1: The resolution status for {call_id} is {status}."
        return f"Sorry, I can't find record {call_id}."
    
    # Tool 2 Sentiment Summary
    def get_sentiment_summary(self, call_id):
        row = self.df[self.df['Call ID'] == call_id]
        if not row.empty:
            outcome_text = row['Outcome'].values[0].lower()
            if "unresolved" in outcome_text or "escalated" in outcome_text:
                return f"Sentiment is Negative (Reason: status is {outcome_text})."
            else:                   
                return f"Sentiment is Positive/Neutral (Reason: status is {outcome_text})."
        return f"Sorry, I can't find record {call_id} "

    # Agent Loop
    def ask(self, user_msg):
        msg = user_msg.lower()
        
        match = re.search(r'CALL_\d{3}', user_msg.upper())          
        cid = match.group(0) if match else None
       
        #  To check Status
        if cid and any(x in msg for x in ["status", "outcome", "resolved"]):
            return self.get_call_outcome(cid)
        
        #  To check Sentiment
        if cid and "sentiment" in msg:
            return self.get_sentiment_summary(cid)

        # Unresolved Summary
        if "unresolved" in msg or "summary" in msg or "escalated" in msg:
            unresolved_calls = self.df[self.df['Outcome'].str.contains('Unresolved|Escalated', case=False)]
            
            context_text = ""
            for index, r in unresolved_calls.iterrows():
                context_text += f"{r['Call ID']}: {r['Customer Complaint / Query']}\n"
            
            prompt = f"Summarize the main issues in these unresolved calls:\n{context_text}"
            try:
                response = model_ai.generate_content(prompt)
                return response.text
            except:
                return "API Quota reached , try again."

        #  RAG Pipeline 
    
        if cid:
            target_row = self.df[self.df['Call ID'] == cid]
            if not target_row.empty:
                row = target_row.iloc[0]
                context = f"ID: {row['Call ID']} | Issue: {row['Customer Complaint / Query']} | Action: {row['Agent Action']}"
            else:
                return f"I couldn't find any data for {cid}."
        else:
           
            query_vector = embed_model.encode([user_msg])
            scores = cosine_similarity(query_vector, self.vectors)
            best_idx = scores.argmax()
            row = self.df.iloc[best_idx]
            context = f"ID: {row['Call ID']} | Issue: {row['Customer Complaint / Query']} | Action: {row['Agent Action']}"
        
      
        final_prompt = f"Data: {context}\nQuestion: {user_msg}\nAnswer shortly based ONLY on provided data:"
        
        try:
            res = model_ai.generate_content(final_prompt)
            return res.text
        except:
            return "API Error, try again."

if __name__ == "__main__":
    bot = CallAgent('data.csv')
    
    # Example 1
    print("\nQ: What happened in CALL_003?")
    print("A:", bot.ask("What happened in CALL_003?"))

    # Example 2
    print("\nQ: Give me a summary of unresolved calls")
    print("A:", bot.ask("Give me a summary of unresolved calls"))

    # Example 3
    print("\nQ: What was the sentiment in CALL_005?")
    print("A:", bot.ask("What was the sentiment in CALL_005?"))
