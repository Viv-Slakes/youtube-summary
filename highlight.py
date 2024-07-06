from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

def parse_vtt_file(caption_file):
    with open(caption_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    timestamps = []
    subtitles = []

    for line in lines:
        line = line.strip()
        if '-->' in line:
            timestamps.append(line.strip())
        elif line:
            subtitles.append(line)
    
    subtitle_pairs = list(zip(timestamps, subtitles))
    return subtitle_pairs
def predict_highlight_scores(subtitle_pairs, model, tokenizer):
    results = []
    
    for timestamp, subtitle in subtitle_pairs:
        inputs = tokenizer(subtitle, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits.squeeze()
        
        # Check if logits represent binary classification (single output) or multi-class
        if logits.dim() == 0 or logits.size(0) == 1:  # Binary classification or single output
            # For binary classification, use sigmoid to get the probability of the positive class
            highlight_score = torch.sigmoid(logits).item()
        else:  # Multi-class classification
            # Assuming 1 corresponds to the highlight class
            highlight_score = torch.softmax(logits, dim=-1)[1].item()
        
        results.append((timestamp, subtitle, highlight_score))
    
    return results
def find_best_highlight(subtitle_results):
    best_subtitle = max(subtitle_results, key=lambda x: x[2])
    return best_subtitle

def timestamp_to_seconds(timestamp):
    # Split the timestamp by ':' and '.' to extract hours, minutes, seconds, and milliseconds
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    
    # Split the seconds part to separate seconds and milliseconds
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    
    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds

def generate_highlights(caption_file, highlight_model, video_url):
    
    model_name = highlight_model
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    subtitle_pairs = parse_vtt_file(caption_file)
    subtitle_results = predict_highlight_scores(subtitle_pairs, model, tokenizer)
    best_highlight = find_best_highlight(subtitle_results)

    best_timestamp = best_highlight[0]

    
    seconds = timestamp_to_seconds(best_timestamp)

    timestamp = f"{video_url}&t={seconds}s"
    return timestamp