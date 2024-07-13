import os
import json
from collections import defaultdict

def convert_iob_to_json(iob_data, language):
    json_outputs = []
    current_sentence = []
    current_entities = defaultdict(list)
    current_entity = []
    current_label = None
    sentence_id = None
    domain = None

    for line in iob_data.strip().split('\n'):
        line = line.strip()
        if line.startswith('# id'):
            if current_sentence:
                json_outputs.append(create_json_output(current_sentence, current_entities, sentence_id, domain, language))
            parts = line.split('\t')
            sentence_id = parts[0].split()[2]
            domain = parts[1].split('=')[1]
            current_sentence = []
            current_entities = defaultdict(list)
            current_entity = []
            current_label = None
            continue

        if not line:
            continue

        parts = line.split()
        if len(parts) != 4:
            continue

        word, _, _, label = parts
        current_sentence.append(word)

        if label.startswith('B-'):
            if current_entity:
                current_entities[current_label].append(" ".join(current_entity))
            current_label = label[2:]
            current_entity = [word]
        elif label.startswith('I-') and current_label:
            current_entity.append(word)
        else:
            if current_entity:
                current_entities[current_label].append(" ".join(current_entity))
                current_entity = []
            current_label = None

    if current_sentence:
        if current_entity:
            current_entities[current_label].append(" ".join(current_entity))
        json_outputs.append(create_json_output(current_sentence, current_entities, sentence_id, domain, language))

    return json_outputs

def create_json_output(sentence, entities, sentence_id, domain, language):
    json_output = {
        "ids": [sentence_id],
        "task_id": "CoNLL03_NER",
        "scorer_cls": "src.tasks.conll03.scorer.CoNLL03EntityScorer",
        "labels": [],
        "text": " ".join(sentence),
        "unlabelled_sentence": " ".join(sentence),
        "language": language,
        "domain": domain,
        "task": f"conll03nom.{language}.ner"
    }

    labels = []
    for entity, spans in entities.items():
        for span in spans:
            labels.append(f"{entity}(span=\"{span}\")")
    json_output["labels"] = f"[{', '.join(labels)}]"

    return json_output

def read_iob_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_new_filename(old_filename):
    parts = old_filename.replace('.conll', '').split('-')
    if len(parts) == 2:
        language, split = parts
        return f"multiconer2.{language.lower()}.ner.{split.lower()}.jsonl"
    return old_filename.replace('.conll', '.jsonl')

def process_file(input_file_path, output_dir):
    print(f"Processing file: {input_file_path}")
    iob_data = read_iob_file(input_file_path)
    base_name = os.path.basename(input_file_path)
    language, _ = base_name.replace('.conll', '').split('-')
    json_outputs = convert_iob_to_json(iob_data, language)
    
    new_file_name = get_new_filename(base_name)
    json_file_path = os.path.join(output_dir, new_file_name)
    
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        for json_output in json_outputs:
            json_file.write(json.dumps(json_output, ensure_ascii=False) + '\n')
    print(f"JSON output saved to: {json_file_path}")

def process_all_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.conll'):
                input_file_path = os.path.join(root, file)
                process_file(input_file_path, output_dir)

# Directory paths
input_directory_path = './GoLLIE/data/processed_w_examples/multiconer2'
output_directory_path = './GoLLIE/data/processed_w_examples/multiconer2'
process_all_files(input_directory_path, output_directory_path)
