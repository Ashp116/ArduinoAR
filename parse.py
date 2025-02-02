import re

def parse_file(filename):
    data = {}
    current_section = None
    pattern = re.compile(r"\[(.*?)\](?:\s*=\s*(.*))?")

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip empty lines and comments

            match = pattern.match(line)
            if match:
                key, value = match.groups()
                if value is not None:
                    data[key] = value  # Key-value pair
                else:
                    current_section = key
                    data[current_section] = []  # Initialize section as list
            elif current_section:
                line = re.sub(r"^\d+\.\s+", "", line)  # Remove numbering
                parts = line.split(":")
                component = parts[0].strip()
                if len(parts) > 1:
                    value = parts[1].strip()
                    if value.lower().startswith("connect"):
                        _, *connections = value.replace("to", "").split()
                        data[current_section].append({"connect": connections})
                    else:
                        data[current_section].append({component: value})
                else:
                    data[current_section].append(component)

    return data



