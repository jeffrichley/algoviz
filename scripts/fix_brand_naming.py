#!/usr/bin/env python3
"""Fix ALGOViz brand naming consistency throughout the codebase.

This script corrects common typos and inconsistencies in the ALGOViz brand name,
ensuring consistent usage across all files while preserving technical identifiers.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.table import Table

console = Console()


class BrandNameFixer:
    """Fixes ALGOViz brand naming inconsistencies throughout the codebase."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.fixes_made = 0
        self.files_processed = 0
        self.console = Console()
        
        # Define correction patterns - order matters!
        # Format: (pattern, replacement, description)
        self.corrections = [
            # FIRST: Preserve technical identifiers (must come before general corrections)
            (r'\bagloviz\.', 'agloviz.', 'Preserve package name'),
            (r'\bagloviz_', 'agloviz_', 'Preserve module names'),
            (r'\bagloviz-', 'agloviz-', 'Preserve CLI/package names'),
            (r'"agloviz"', '"agloviz"', 'Preserve quoted package names'),
            (r"'agloviz'", "'agloviz'", 'Preserve quoted package names'),
            (r'`agloviz`', '`agloviz`', 'Preserve code blocks'),
            (r'agloviz render', 'agloviz render', 'Preserve CLI commands'),
            (r'agloviz config', 'agloviz config', 'Preserve CLI commands'),
            (r'agloviz preview', 'agloviz preview', 'Preserve CLI commands'),
            (r'agloviz version', 'agloviz version', 'Preserve CLI commands'),
            
            # THEN: Brand name corrections (only in non-technical contexts)
            (r'(?<![\w.])\bAGLOViz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAGLoViz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAGLoviz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAglOViz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAGLOviz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAlgoViz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bALGOviz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bAlgoviz\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            (r'(?<![\w.])\bALGOVIZ\b(?![\w.])', 'ALGOViz', 'ALGOViz → ALGOViz'),
            
            # Special markdown and comment contexts
            (r'\*\*ALGOViz\*\*', '**ALGOViz**', 'Fix markdown bold'),
            (r'# ALGOViz', '# ALGOViz', 'Fix comments'),
            (r'ALGOViz_([A-Z])', r'ALGOViz_\1', 'Preserve ALGOViz_ prefixes'),
        ]
        
        # Files to exclude from processing
        self.exclude_patterns = [
            r'\.git/',
            r'\.venv/',
            r'__pycache__/',
            r'\.pytest_cache/',
            r'\.mypy_cache/',  # Exclude mypy cache
            r'htmlcov/',
            r'dist/',
            r'build/',
            r'\.egg-info/',
            r'node_modules/',
            r'coverage\.xml',
            r'\.coverage',
            r'uv\.lock',
        ]
        
        # File extensions to process
        self.include_extensions = {
            '.py', '.md', '.yaml', '.yml', '.toml', '.txt', '.rst',
            '.json', '.cfg', '.ini', '.sh', '.bash', '.zsh'
        }
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed for brand name fixes."""
        # Check if file should be excluded
        path_str = str(file_path)
        for exclude_pattern in self.exclude_patterns:
            if re.search(exclude_pattern, path_str):
                return False
        
        # Check if file extension should be included
        return file_path.suffix.lower() in self.include_extensions
    
    def find_files_to_process(self, root_dir: Path) -> List[Path]:
        """Find all files that should be processed."""
        files = []
        
        for file_path in root_dir.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                files.append(file_path)
        
        return sorted(files)
    
    def analyze_file(self, file_path: Path) -> List[Tuple[int, str, str, str]]:
        """Analyze a file for brand naming issues.
        
        Returns:
            List of (line_number, original_line, corrected_line, description)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError):
            return []  # Skip binary files or permission issues
        
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            corrected_line = line
            
            # Apply each correction pattern
            for pattern, replacement, description in self.corrections:
                if re.search(pattern, corrected_line):
                    new_line = re.sub(pattern, replacement, corrected_line)
                    if new_line != corrected_line:
                        corrected_line = new_line
                        issues.append((line_num, original_line.strip(), corrected_line.strip(), description))
                        break  # Only report first change per line
        
        return issues
    
    def fix_file(self, file_path: Path) -> int:
        """Fix brand naming issues in a file.
        
        Returns:
            Number of fixes made
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return 0
        
        original_content = content
        fixes_in_file = 0
        
        # Apply all correction patterns
        for pattern, replacement, description in self.corrections:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                matches = len(re.findall(pattern, content))
                fixes_in_file += matches
                content = new_content
        
        # Write back if changes were made and not in dry-run mode
        if content != original_content and not self.dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return fixes_in_file
    
    def run_analysis(self, root_dir: Path) -> Dict[str, List[Tuple[int, str, str, str]]]:
        """Run analysis on all files and return issues found."""
        files = self.find_files_to_process(root_dir)
        all_issues = {}
        
        with Progress() as progress:
            task = progress.add_task("Analyzing files...", total=len(files))
            
            for file_path in files:
                issues = self.analyze_file(file_path)
                if issues:
                    all_issues[str(file_path)] = issues
                
                progress.update(task, advance=1)
        
        return all_issues
    
    def run_fixes(self, root_dir: Path) -> Dict[str, int]:
        """Run fixes on all files and return fix counts."""
        files = self.find_files_to_process(root_dir)
        fix_counts = {}
        
        with Progress() as progress:
            task = progress.add_task(
                "Fixing files..." if not self.dry_run else "Analyzing files...",
                total=len(files)
            )
            
            for file_path in files:
                fixes = self.fix_file(file_path)
                if fixes > 0:
                    fix_counts[str(file_path)] = fixes
                    self.fixes_made += fixes
                
                self.files_processed += 1
                progress.update(task, advance=1)
        
        return fix_counts
    
    def display_analysis_results(self, issues: Dict[str, List[Tuple[int, str, str, str]]]) -> None:
        """Display analysis results in a formatted table."""
        if not issues:
            console.print("✅ [bold green]No brand naming issues found![/bold green]")
            return
        
        console.print(f"\n🔍 [bold]Found brand naming issues in {len(issues)} files:[/bold]\n")
        
        for file_path, file_issues in issues.items():
            console.print(f"📄 [bold blue]{file_path}[/bold blue]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Line", style="dim", width=6)
            table.add_column("Original", style="red")
            table.add_column("Corrected", style="green")
            table.add_column("Type", style="blue")
            
            for line_num, original, corrected, description in file_issues:
                table.add_row(
                    str(line_num),
                    original[:50] + "..." if len(original) > 50 else original,
                    corrected[:50] + "..." if len(corrected) > 50 else corrected,
                    description
                )
            
            console.print(table)
            console.print()
    
    def display_fix_results(self, fix_counts: Dict[str, int]) -> None:
        """Display fix results summary."""
        if not fix_counts:
            console.print("✅ [bold green]No fixes needed![/bold green]")
            return
        
        mode = "DRY RUN - " if self.dry_run else ""
        console.print(f"\n🔧 [bold]{mode}Fix Results:[/bold]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="blue")
        table.add_column("Fixes", style="green", justify="right")
        
        for file_path, count in sorted(fix_counts.items()):
            table.add_row(file_path, str(count))
        
        console.print(table)
        
        total_fixes = sum(fix_counts.values())
        total_files = len(fix_counts)
        
        console.print(f"\n📊 [bold]Summary:[/bold]")
        console.print(f"  • Files processed: {self.files_processed}")
        console.print(f"  • Files with issues: {total_files}")
        console.print(f"  • Total fixes: {total_fixes}")
        
        if self.dry_run:
            console.print(f"\n💡 [bold blue]Run without --dry-run to apply fixes[/bold blue]")


def main():
    """Main entry point for the brand name fixer script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix ALGOViz brand naming consistency throughout the codebase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true", 
        help="Only analyze and show issues, don't fix them"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd(),
        help="Root directory to process (default: current directory)"
    )
    
    args = parser.parse_args()
    
    console.print(Panel(
        "[bold blue]ALGOViz Brand Name Consistency Fixer[/bold blue]\n\n"
        "This script fixes common typos and inconsistencies in the ALGOViz brand name\n"
        "while preserving technical identifiers like package names.",
        title="🏷️ Brand Name Fixer",
        padding=(1, 2),
    ))
    
    if not args.root_dir.exists():
        console.print(f"❌ [bold red]Directory not found:[/bold red] {args.root_dir}")
        sys.exit(1)
    
    fixer = BrandNameFixer(dry_run=args.dry_run or args.analyze_only)
    
    if args.analyze_only:
        console.print("🔍 [bold]Running analysis only...[/bold]\n")
        issues = fixer.run_analysis(args.root_dir)
        fixer.display_analysis_results(issues)
    else:
        console.print(f"🔧 [bold]{'Analyzing' if args.dry_run else 'Fixing'} brand naming issues...[/bold]\n")
        fix_counts = fixer.run_fixes(args.root_dir)
        fixer.display_fix_results(fix_counts)
    
    if fixer.fixes_made > 0 and not args.dry_run:
        console.print("\n✅ [bold green]Brand naming fixes completed![/bold green]")
        console.print("💡 [dim]Consider running 'just fix' to clean up any formatting issues[/dim]")


if __name__ == "__main__":
    main()
