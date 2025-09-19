from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

device = "cpu"  # Use CPU
model.to(device)

# Simple chat loop
while True:
    user_input = input("You: ")
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    
    reply_ids = model.generate(**inputs, use_cache=False, max_new_tokens=50)
    bot_reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    
    print("Bot:", bot_reply)
