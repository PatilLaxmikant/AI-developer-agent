import os
import subprocess
import platform
import difflib

class ProjectManager:
    def __init__(self, working_dir: str):
        self.working_dir = os.path.abspath(working_dir)
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

    def list_files(self, subdir: str = ".", max_depth: int = 2) -> str:
        """Generates a tree view of the project directory."""
        tree = []
        try:
            start = os.path.normpath(os.path.join(self.working_dir, subdir))
            if not os.path.exists(start):
                return "Error: Directory does not exist."
            
            num_sep_start = start.count(os.sep)
            for root, dirs, files in os.walk(start):
                num_sep = root.count(os.sep)
                if num_sep - num_sep_start >= max_depth:
                    del dirs[:]
                    continue
                
                indent = "  " * (num_sep - num_sep_start)
                tree.append(f"{indent}{os.path.basename(root)}/")
                sub_indent = "  " * (num_sep - num_sep_start + 1)
                for f in files:
                    if not f.startswith('.'): # Ignore hidden files
                        tree.append(f"{sub_indent}{f}")
            return "\n".join(tree)
        except Exception as e:
            return f"Error reading directory: {str(e)}"

    def read_file(self, filepath: str) -> str:
        """Reads content from a file."""
        try:
            full_path = os.path.join(self.working_dir, filepath)
            if not os.path.exists(full_path):
                return f"Error: File not found: {filepath}"
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, filepath: str, content: str, dry_run: bool = False) -> dict:
        """
        Writes content to a file. 
        If dry_run is True, returns the diff instead of writing.
        """
        try:
            full_path = os.path.join(self.working_dir, filepath)
            
            # Calculate Diff
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    old_content = f.readlines()
            else:
                old_content = []
            
            new_content = content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_content, 
                new_content, 
                fromfile=filepath, 
                tofile=filepath, 
                lineterm=''
            )
            diff_text = ''.join(diff)

            if dry_run:
                return {
                    "success": True,
                    "diff": diff_text,
                    "action": "would_write",
                    "path": filepath
                }

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "diff": diff_text,
                "action": "wrote",
                "path": filepath
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_command(self, command: str) -> str:
        """Executes a shell command and returns output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            return output
        except Exception as e:
            return f"Execution Error: {str(e)}"
