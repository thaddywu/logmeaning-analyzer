from glob import glob
import pandas as pd
import re

def extract_variables(text, template):
    text = text.strip(" ")
    # Need to check what happened?
    #  Currently, text seems sometimes start with redundant spaces.

    template = template.replace("<NUM>", "<*>")
    comps = template.split("<*>")
    lens = [len(comp) for comp in comps]
    text_len = len(text)
    def is_matched(text_pos, comp_idx):
        r = text_pos+lens[comp_idx]
        return r <= text_len and text[text_pos:r] == comps[comp_idx]
    def match_dfs(text_pos, comp_idx):
        if is_matched(text_pos, comp_idx):
            r_pos = text_pos+lens[comp_idx]

            if comp_idx + 1 >= len(comps):
                return [] if r_pos == text_len else None
            for pos in range(r_pos, text_len+1):
                if is_matched(pos, comp_idx+1):
                    ret = match_dfs(pos, comp_idx+1)
                    if ret is not None: return [text[r_pos:pos]] + ret
        return None
    
    return match_dfs(0, 0)


import os
for log_structured_path in glob("../loghub/*/*.log_structured.csv"):
    log_structured = pd.read_csv(log_structured_path)
    log_templates = pd.read_csv(log_structured_path.replace(".log_structured", ".log_templates"))

    BENCH = log_structured_path.split("/")[-2]
    os.makedirs(BENCH, exist_ok=True)

    templates_dict = dict() # eventid -> template: String
    for _, row in log_templates.iterrows():
        templates_dict[row["EventId"]] = row["EventTemplate"]

    extracted_vars_dict = {k:[] for k in templates_dict.keys()} # eventid -> [[], ..] : List[List]
    for _, row in log_structured.iterrows():
        extracted_vars = extract_variables(row["Content"], row["EventTemplate"])
        assert extracted_vars is not None, row["Content"] + "\n" + row["EventTemplate"]
        extracted_vars_dict[row["EventId"]] += [extracted_vars]
    
    for eventID, vars in extracted_vars_dict.items():
        template = templates_dict[eventID].replace("<NUM>", "<*>")
        if "<*>" not in template: continue
        if len(vars) == 0: continue

        df = pd.DataFrame(vars, columns=[f"var{i+1}" for i in range(len(vars[0]))])
        df.to_csv(f"{BENCH}/{eventID}.csv", index=False)
    
    
    # print(log_structured[["Content", "EventId", "EventTemplate"]])