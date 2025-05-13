from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline
)
from .config import MODEL_NAME, CACHE_DIR, HUGGINGFACE_TOKEN
import os, torch


tokenizer, model, pipe = None, None, None


def get_model_path():
    safe_name = MODEL_NAME.replace("/", "_")
    return os.path.join(CACHE_DIR, safe_name)

def init_model():

    global tokenizer, model
    if tokenizer is None or model is None:
        model_path = get_model_path()
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            use_auth_token=HUGGINGFACE_TOKEN,
            local_files_only=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            use_auth_token=HUGGINGFACE_TOKEN,
            device_map="auto",
            torch_dtype=torch.float16,
            local_files_only=True
        )

def generate_answer(prompt: str, max_new_tokens: int = 128) -> str:
    init_model()

    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False
    )

    generated_ids = outputs[0][inputs["input_ids"].size(-1):]
    return tokenizer.decode(generated_ids, skip_special_tokens=True)

def get_pipeline():
    """Gibt eine Pipeline für die Textgenerierung zurück"""
    global pipe, tokenizer, model
    
    if pipe is not None:
        return pipe
        
    # Wenn das Modell noch nicht initialisiert ist, initialisiere es
    init_model()
    
    # Erstelle die Pipeline mit dem bereits initialisierten Modell und Tokenizer
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
        trust_remote_code=True
    )
    
    return pipe