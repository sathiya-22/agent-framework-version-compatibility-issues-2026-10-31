import ast
import re
from pathlib import Path
import click

# List of known agent framework top-level modules
# This list can be extended as new frameworks emerge
AGENT_FRAMEWORKS = [
    "langchain",
    "llama_index",
    "marvin",
    "crewai",
    "autogen",
    "guardrails",
    "guidance",
    "agentops", # Example of an agent-ops tool that might be a dependency
]

class AgentFrameworkVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imported_frameworks = set()

    def visit_Import(self, node):
        for alias in node.names:
            self._check_import(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self._check_import(node.module)
        self.generic_visit(node)

    def _check_import(self, module_name):
        if module_name:
            # Check if the top-level module matches any known framework
            top_level_module = module_name.split('.')[0]
            if top_level_module in AGENT_FRAMEWORKS:
                self.imported_frameworks.add(top_level_module)

def parse_requirements_file(file_path: Path) -> dict[str, str]:
    """Parses a requirements.txt file and returns a dict of package_name -> version."""
    dependencies = {}
    if not file_path.exists():
        click.echo(f"Warning: Requirements file not found at {file_path}", err=True)
        return dependencies

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Simple regex to capture package name and version (e.g., package==1.2.3, package>=1.0)
            match = re.match(r"([a-zA-Z0-9._-]+)(==|>=|<=|~=|<|>)?(.*)", line)
            if match:
                pkg_name = match.group(1).lower()
                version_spec = f"{match.group(2) or ''}{match.group(3) or ''}"
                dependencies[pkg_name] = version_spec.strip()
    return dependencies

@click.command()
@click.option('--project-path', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True),
              required=True, help='Path to the root of your agent project source code.')
@click.option('--requirements-file', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
              required=True, help='Path to your project\'s requirements.txt file.')
def main(project_path: str, requirements_file: str):
    """
    Checks an agent project for framework dependency compatibility issues.
    """
    project_path = Path(project_path)
    requirements_file = Path(requirements_file)

    click.echo(f"🔍 Analyzing agent project at {project_path}...")
    click.echo(f"📦 Reading dependencies from {requirements_file}...")

    all_imported_frameworks = set()
    code_files_scanned = 0

    for py_file in project_path.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=py_file)
            visitor = AgentFrameworkVisitor()
            visitor.visit(tree)
            if visitor.imported_frameworks:
                for framework in visitor.imported_frameworks:
                    all_imported_frameworks.add((framework, py_file.relative_to(project_path)))
            code_files_scanned += 1
        except SyntaxError as e:
            click.echo(f"Warning: Could not parse {py_file} due to syntax error: {e}", err=True)
        except Exception as e:
            click.echo(f"Error processing {py_file}: {e}", err=True)

    project_dependencies = parse_requirements_file(requirements_file)

    click.echo("\nDetected Framework Imports:")
    if not all_imported_frameworks:
        click.echo("  No known agent framework imports detected.")
    else:
        for framework, file_path in sorted(list(all_imported_frameworks)):
            click.echo(f"- {framework} (imported in {file_path})")

    click.echo("\nProject Dependencies (from requirements.txt):")
    if not project_dependencies:
        click.echo("  No dependencies found in requirements.txt or file is empty.")
    else:
        for pkg, version_spec in sorted(project_dependencies.items()):
            click.echo(f"- {pkg}{version_spec}")

    click.echo("\nPotential Version Inconsistencies or Warnings:")
    warnings_found = False
    for framework_name, _ in sorted(list(all_imported_frameworks)):
        # Normalize framework names for lookup in requirements.txt
        # e.g., 'llama_index' in code vs 'llama-index' in requirements.txt
        normalized_framework_name = framework_name.replace('_', '-')
        
        if normalized_framework_name in project_dependencies:
            version_spec = project_dependencies[normalized_framework_name]
            # This is a simplified check. A real tool might compare against a database of
            # known breaking changes for specific versions.
            click.echo(f"- {framework_name}: Found '{normalized_framework_name}{version_spec}' in requirements.txt. "
                       f"Consider checking for newer versions or known breaking changes if encountering issues with latest framework code.")
            warnings_found = True
        else:
            click.echo(f"- {framework_name}: Imported but not found in requirements.txt. "
                       f"This could indicate a missing dependency or an indirect dependency not explicitly listed.")
            warnings_found = True

    if not warnings_found:
        click.echo("  No obvious inconsistencies detected based on current analysis.")

    click.echo("\nAnalysis Complete. Review the output for potential dependency issues.")

if __name__ == '__main__':
    main()
