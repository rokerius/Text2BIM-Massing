# Copyright (c) 2024 dcy0577. MIT; see LICENSE.

import re
import types


def safe_encode(obj):
    if isinstance(obj, types.ModuleType):
        return None  # or return a string like '<<module>>'
    try:
        return obj.__dict__
    except AttributeError:
        return str(obj)

def remove_last_human_message_with_regex(text):
    # Regex pattern to find a 'Human:' message followed by any text, including new lines up to the end of the string
    # and ensuring it's the last thing in the string with optional preceding whitespace or line breaks
    pattern = r"\s*\nUser: [^\n]*\s*\Z|\A\s*User: [^\n]*\s*\Z"
    
    # Use re.sub to replace the found pattern with an empty string
    new_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
    
    return new_text

def clean_code_for_chat_extend(result):
    lines = result.split("\n")
    idx = 0
    explanations = []
    codes = []
    while idx < len(lines):
        while idx < len(lines) and not lines[idx].lstrip().startswith("```"):
            idx += 1
        explanation = "\n".join(lines[:idx]).strip()
        if explanation:  # Only append if there is content
            explanations.append(explanation)
        if idx == len(lines):
            break
        idx += 1
        start_idx = idx
        while idx < len(lines) and not lines[idx].lstrip().startswith("```"):
            idx += 1
        code = "\n".join(lines[start_idx:idx]).strip()
        if code:  # Only append if there is content
            codes.append(code)
        lines = lines[idx+1:]
        idx = 0
    return explanations, codes
