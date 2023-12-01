from glob import glob
import pandas as pd
import re
import openai, json, os, hashlib

class chatGPT:
    def __init__(self) -> None:
        openai.api_key = "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"

    def invoke(self, prompt):
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        chatgpt_response = str(result)
        result_json = json.loads(chatgpt_response)
        content = result_json["choices"][0]["message"]["content"]

        return instances, result_json["usage"]["total_tokens"]

cgpt = chatGPT()

for log_structured_path in glob("../loghub/*/*.log_structured.csv"):
    #log_structured = pd.read_csv(log_structured_path)
    log_templates = pd.read_csv(log_structured_path.replace(".log_structured", ".log_templates"))

    BENCH = log_structured_path.split("/")[-2]

    if BENCH != "Android": continue

    templates_dict = dict() # eventid -> template: String
    for _, row in log_templates.iterrows():
        templates_dict[row["EventId"]] = row["EventTemplate"]
    
    for E_path in glob(f"./{BENCH}/E*.csv"):
        with open(E_path, "r") as f:
            raw_data = [row for row in f.readlines() if row.strip()]

        EventId = E_path.split("/")[-1][:-4]
        template = templates_dict[EventId]

        csv_str = "".join(raw_data[0:]) + "\n"

        prompt = f"""I'll give you several example logs generated from the same log template \"{template}\"
Each <*> is a placeholder for a variable without its name.
I have extracted out the {len(raw_data[0].split(","))} values from each of the {len(raw_data)-1} logs out, and put them in the end.
Please analyze those values along with the given template, and guess the meaning of each variable in the template.
Please answer in two lines: the first line is your guessed meanings, delimited by comma. The second line is your guess about whether each variables is sensitive or not. Please write T as sensitive, F as non-sensitive. Don't answer anything else!
Extracted out values:
{csv_str}"""

        with open(f"{BENCH}/{EventId}.prompt", "w") as f:
            f.write(prompt)
        #answer = cgpt.invoke(prompt)