import re

def translate_command(command):
    # Basic command translations
    translations = {
        'echo': lambda args: f'print({args})',
        'cd': lambda args: f'os.chdir({args})',
        'ls': lambda args: f'print(os.listdir({args if args else "."}))',
        'if': lambda args: f'if {args}:',
        'fi': lambda args: '',  # 'fi' is just the end of an 'if' block in shell
        'for': lambda args: f'for {args}:',
        'done': lambda args: '',  # 'done' is just the end of a loop block in shell
        'while': lambda args: f'while {args}:'
    }

    command_parts = command.split(maxsplit=1)
    cmd = command_parts[0]
    args = command_parts[1] if len(command_parts) > 1 else ''

    # Handle simple translations directly
    if cmd in translations:
        return translations[cmd](args)

    # Handle unsupported commands
    return f"# Unsupported command: {command}"

def convert_sh_to_py(sh_file, py_file):
    with open(sh_file, 'r') as infile, open(py_file, 'w') as outfile:
        outfile.write("#!/usr/bin/env python3\n")
        outfile.write("import os\n\n")
        
        for line in infile:
            line = line.strip()
            if line:
                translated_line = translate_command(line)
                outfile.write(translated_line + "\n")

# Example usage
convert_sh_to_py('script.sh', 'script.py')


