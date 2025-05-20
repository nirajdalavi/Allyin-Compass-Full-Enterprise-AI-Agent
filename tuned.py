from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel, PeftConfig

# 1. Load the base model
base_model_id = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_id)

# 2. Load the LoRA adapter
adapter_path = "models/lora_adapter"  # or absolute path if needed
model = PeftModel.from_pretrained(base_model, adapter_path)

# 3. Set to evaluation mode
model.eval()

# 4. Inference function
def run_inference(query: str):
    prompt = f"### Question:\n{query}\n\n### Answer:\n"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example
print(run_inference("What equipment was used in the ZY-102 experiment?"))