import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\0e07d07b-a49a-4a13-8476-76e7c56c9494\.system_generated\logs\transcript.jsonl"
if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                content = data.get("content")
                typ = data.get("type")
                if typ == "USER_INPUT":
                    print(f"Step {data.get('step_index')}: {content}")
                    print("-" * 50)
            except Exception as e:
                pass
else:
    print("Transcript not found")
