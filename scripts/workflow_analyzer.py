#!/usr/bin/env python3
import os
import yaml
import re


class GitHubWorkflowAnalyzer:
    def __init__(self):
        self.workflows_dir = '.github/workflows'
        self.issues = []

    def analyze_all_workflows(self):
        """Analyze all workflow files in the repository"""
        if not os.path.exists(self.workflows_dir):
            print("No workflows directory found")
            return

        for filename in os.listdir(self.workflows_dir):
            if filename.endswith(('.yml', '.yaml')):
                self.analyze_workflow(os.path.join(
                    self.workflows_dir, filename))

        if self.issues:
            print(f"Found {len(self.issues)} issues in workflows")
            for issue in self.issues:
                print(f"- {issue}")
        else:
            print("✅ No issues found in workflows")

    def analyze_workflow(self, filepath):
        """Analyze a single workflow file for best practices"""
        with open(filepath, 'r') as f:
            try:
                workflow = yaml.safe_load(f)

                # Check for pinned action versions (avoid using 'main' or 'master')
                self._check_pinned_actions(workflow, filepath)

                # Check for timeout settings
                self._check_timeouts(workflow, filepath)

                # Check for permissions (principle of least privilege)
                self._check_permissions(workflow, filepath)

            except yaml.YAMLError as e:
                self.issues.append(f"Invalid YAML in {filepath}: {e}")

    def _check_pinned_actions(self, workflow, filepath):
        """Check if actions use pinned versions instead of branches"""
        for job_id, job in workflow.get('jobs', {}).items():
            for step in job.get('steps', []):
                if 'uses' in step:
                    action_ref = step['uses']
                    if '@' in action_ref:
                        ref = action_ref.split('@')[1]
                        if ref in ('main', 'master'):
                            self.issues.append(
                                f"{filepath}: Job '{job_id}' uses unpinned action reference: {action_ref}"
                            )

    def _check_timeouts(self, workflow, filepath):
        """Check if jobs have timeout settings"""
        for job_id, job in workflow.get('jobs', {}).items():
            if 'timeout-minutes' not in job:
                self.issues.append(
                    f"{filepath}: Job '{job_id}' doesn't have a timeout set"
                )

    def _check_permissions(self, workflow, filepath):
        """Check if workflow defines explicit permissions"""
        if 'permissions' not in workflow:
            self.issues.append(
                f"{filepath}: No top-level permissions defined"
            )


if __name__ == "__main__":
    analyzer = GitHubWorkflowAnalyzer()
    analyzer.analyze_all_workflows()
