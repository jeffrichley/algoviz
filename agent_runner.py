#!/usr/bin/env python3
"""
AI Agent Runner - Process files using Cursor CLI
"""
import json
import subprocess
import sys
from pathlib import Path

def run_cursor_agent(json_file_path, target_file_path):
    """Run Cursor CLI agent on a file."""
    
    # Generate the prompt
    prompt_gen = Path(__file__).parent / "agent_prompt_generator.py"
    result = subprocess.run([
        sys.executable, str(prompt_gen), json_file_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error generating prompt: {result.stderr}")
        return False
    
    prompt = result.stdout
    
    # Run Cursor CLI
    try:
        print(f"🤖 Running Cursor agent on {target_file_path}...")
        
        # Use Cursor CLI agent mode
        cursor_result = subprocess.run([
            "cursor-agent", "--print", 
            prompt,
            target_file_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if cursor_result.returncode == 0:
            print(f"✅ Successfully processed {target_file_path}")
            # Print a sample of the output for debugging
            if cursor_result.stdout:
                print(f"📝 Output preview: {cursor_result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Cursor CLI failed: {cursor_result.stderr}")
            if cursor_result.stdout:
                print(f"📝 Output: {cursor_result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout processing {target_file_path}")
        return False
    except FileNotFoundError:
        print("❌ cursor-agent not found. Please install Cursor CLI first.")
        return False
    except Exception as e:
        print(f"❌ Error running Cursor CLI: {e}")
        return False

def process_agent_work(agent_id):
    """Process all work for a specific agent."""
    
    agent_dir = Path(f"issues/assigned/agent_{agent_id}")
    todo_dir = agent_dir / "todo"
    done_dir = agent_dir / "done"
    
    if not todo_dir.exists():
        print(f"❌ Agent {agent_id} todo directory not found")
        return
    
    # Get all JSON files in todo
    json_files = list(todo_dir.glob("*.json"))
    
    if not json_files:
        print(f"📭 Agent {agent_id} has no work to do")
        return
    
    print(f"🤖 Agent {agent_id} processing {len(json_files)} files...")
    
    processed = 0
    failed = 0
    
    for json_file in json_files:
        # Load the JSON to get the target file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        target_file = data.get("file")
        if not target_file or not Path(target_file).exists():
            print(f"⚠️  Skipping {json_file.name} - target file not found: {target_file}")
            continue
        
        # Process the file
        if run_cursor_agent(json_file, target_file):
            # Move to done
            done_file = done_dir / json_file.name
            json_file.rename(done_file)
            processed += 1
            print(f"✅ Moved {json_file.name} to done")
        else:
            failed += 1
            print(f"❌ Failed to process {json_file.name}")
    
    print(f"🎯 Agent {agent_id} completed:")
    print(f"   • Processed: {processed}")
    print(f"   • Failed: {failed}")
    print(f"   • Remaining: {len(list(todo_dir.glob('*.json')))}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python agent_runner.py <agent_id>")
        print("Example: python agent_runner.py 1")
        sys.exit(1)
    
    try:
        agent_id = int(sys.argv[1])
        process_agent_work(agent_id)
    except ValueError:
        print("Error: Agent ID must be a number")
        sys.exit(1)

if __name__ == "__main__":
    main()
