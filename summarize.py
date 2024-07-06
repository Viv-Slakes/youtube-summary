import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import re
from transformers import pipeline

def split_into_chunks(text, chunk_size=1024):
    # Split the text by spaces to avoid breaking words
    words = text.split(' ')
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    # Add the last chunk if any
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def summarize_text(caption_file, summarization_model):
    
    with open(caption_file, 'r', encoding='utf-8') as file:
        file_content = file.read()

    captions = re.findall(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n(.+?)(?=\n\n|\Z)', file_content, re.DOTALL)
    captions_text = ' '.join(captions).replace('\n', ' ')

    summarizer = pipeline("summarization", device=0, model=summarization_model)


    # Split text into chunks
    chunks = split_into_chunks(captions_text, 1024)

    summaries = []
    for chunk in chunks:
        # Generate summary for each chunk
        summary = summarizer(chunk, max_length=50, min_length=25, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    # Combine the summaries
    summary = ' '.join(summaries)
    summary = summary.replace('. ', '.\n')
    summary = summary.replace('?', '?\n')
    summary = summary.replace('!', '!\n')
    return summary
