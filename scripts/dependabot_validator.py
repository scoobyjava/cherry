#!/usr/bin/env python3
import os
import json
import yaml
import jsonschema
from github_schema_validator import GitHubSchemaValidator

class DependabotValidator:
    def __init__(self, schema_validator):
        self.schema_validator = schema_validator
        self.dependabot_file = '.github/dependabot.yml'
        
    def validate(self):
        """Validate dependabot configuration and check for common issues"""
        if not os.path.exists(self.dependabot_file):
            print("⚠️ No dependabot.yml file found")
            return False
            
        with open(self.dependabot_file, 'r') as f:
            try:
                config = yaml.safe_load(f)
                
                # Check for duplicate package ecosystems
                ecosystems = {}
                for update in config.get('updates', []):
                    ecosystem = update.get('package-ecosystem')
                    directory = update.get('directory', '/')
                    key = f"{ecosystem}:{directory}"
                    
                    if key in ecosystems:
                        print(f"⚠️ Duplicate ecosystem configuration: {key}")
                    
                    ecosystems[key] = True
                    
                # Check for invalid registries
                if 'registries' in config:
                    for reg_name, reg_info in config['registries'].items():
                        if 'type' not in reg_info:
                            print(f"⚠️ Missing registry type for {reg_name}")
                        if 'url' not in reg_info:
                            print(f"⚠️ Missing URL for registry {reg_name}")
                
                return True
            except yaml.YAMLError as e:
                print(f"❌ Invalid YAML in dependabot.yml: {e}")
                return False

if __name__ == "__main__":
    validator = GitHubSchemaValidator()
    dependabot_validator = DependabotValidator(validator)
    dependabot_validator.validate()