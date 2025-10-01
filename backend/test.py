import os
import re

def extract_permissions_from_routes(directory):
    permissions = set()
    permission_pattern = re.compile(r"@permissions\.has_permission\(\[(.*?)\]\)")
    blueprint_pattern = re.compile(r"__blueprint__\s*=\s*'([\w]+)'")
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "routes.py":
                file_path = os.path.join(root, file)
                blueprint = None
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        blueprint_match = blueprint_pattern.search(line)
                        if blueprint_match:
                            blueprint = blueprint_match.group(1)
                        match = permission_pattern.search(line)
                        if match and blueprint:
                            permission_list = set(match.group(1).replace("'", "").split(', '))
                            for permission in permission_list:
                                permissions.add((blueprint, permission))
    
    return permissions

# Example usage
directory_path = "app"  # Change this to your actual project path
permissions = extract_permissions_from_routes(directory_path)

unique_permissions = set(permissions)
for model, name in unique_permissions:
    print(f"{{'model':'{model}','name':'{name}'}},")
