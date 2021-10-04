import json
import os


def run(mail_data):
    output_dir = os.getenv('OUTPUT_DIR')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, f"{mail_data['to']}.json")
    with open(file_path, 'w+') as f:
        f.write(json.dumps(mail_data, sort_keys=True, indent=4))
