import argparse
import sys
import tokenize
import io
import re
import os

def remove_python_comments(source):
    """
    Removes comments from Python source code, preserving docstrings and shebangs.
    """
    # Tokenize requires bytes
    try:
        source_bytes = source.encode('utf-8')
    except UnicodeEncodeError:
        return source

    io_obj = io.BytesIO(source_bytes)
    
    try:
        tokens = list(tokenize.tokenize(io_obj.readline))
    except tokenize.TokenError:
        return source

    lines = source.splitlines(keepends=True)
    modifications = []
    
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            if tok.start[0] == 1 and tok.string.startswith("#!"):
                continue
            if tok.start[0] <= 2 and "coding:" in tok.string:
                continue

            start_line, start_col = tok.start
            end_line, end_col = tok.end
            modifications.append((start_line - 1, start_col, end_line - 1, end_col))

    if not modifications:
        return source

    mods_by_line = {}
    for m in modifications:
        line_idx = m[0]
        if line_idx not in mods_by_line:
            mods_by_line[line_idx] = []
        mods_by_line[line_idx].append(m)

    new_lines = []
    for i, line in enumerate(lines):
        if i in mods_by_line:
            current_mods = sorted(mods_by_line[i], key=lambda x: x[1], reverse=True)
            line_chars = list(line)
            for _, start_col, _, end_col in current_mods:
                del line_chars[start_col:end_col]
            
            new_line_content = "".join(line_chars)
            if new_line_content.endswith('\n') or new_line_content.endswith('\r'):
                content = new_line_content.rstrip('\r\n')
                ending = new_line_content[len(content):]
                content = content.rstrip()
                new_line_content = content + ending
            else:
                new_line_content = new_line_content.rstrip()

            new_lines.append(new_line_content)
        else:
            new_lines.append(line)

    return "".join(new_lines)

def remove_c_style_comments(source):
    """
    Removes // comments from C-style languages (C, C++, Java, JS, TS, Rust, Go, etc.)
    Preserves:
    - Strings ("...", '...')
    - Backtick strings (`...`) (JS, Go)
    - Doc comments (///..., //!..., /**...*/)
    - Block comments (/*...*/)
    """
    
    pattern_string_double = r'"(?:\\.|[^"\\])*"'
    pattern_string_single = r"'(?:\\.|[^'\\])*'"
    pattern_string_backtick = r'`(?:\\.|[^`\\])*`'
    
    pattern_doc_line = r'//[/!].*?$' 
    pattern_doc_block = r'/\*[\*!].*?\*/'
    
    pattern_comment_inline = r'//.*?$'
    
    pattern = re.compile(
        f"({pattern_string_double})|({pattern_string_single})|({pattern_string_backtick})|" +
        f"({pattern_doc_line})|({pattern_doc_block})|({pattern_comment_inline})",
        re.MULTILINE | re.DOTALL
    )

    def replacer(match):
        if match.group(1) or match.group(2) or match.group(3):
            return match.group(0)
        if match.group(4) or match.group(5):
            return match.group(0)
        if match.group(6):
            return ""
        return match.group(0)

    cleaned = pattern.sub(replacer, source)
    
    final_lines = []
    for line in cleaned.splitlines(keepends=True):
        if line.strip() == "":
             final_lines.append(line)
             continue
        
        if line.endswith('\n') or line.endswith('\r'):
            content = line.rstrip('\r\n')
            ending = line[len(content):]
            content = content.rstrip() 
            final_lines.append(content + ending)
        else:
            final_lines.append(line.rstrip())
            
    return "".join(final_lines)

def remove_hash_comments(source):
    """
    Removes # comments for Shell, YAML, Ruby, etc.
    """
    pattern_string_double = r'"(?:\\.|[^"\\])*"'
    pattern_string_single = r"'(?:\\.|[^'\\])*'"
    pattern_comment = r'#.*?$'
    
    pattern = re.compile(
        f"({pattern_string_double})|({pattern_string_single})|({pattern_comment})",
        re.MULTILINE
    )
    
    def replacer(match):
        if match.group(1) or match.group(2):
            return match.group(0)
        if match.group(3):
            return ""
        return match.group(0)

    cleaned = pattern.sub(replacer, source)
    
    final_lines = []
    for line in cleaned.splitlines(keepends=True):
         if line.endswith('\n') or line.endswith('\r'):
            content = line.rstrip('\r\n')
            ending = line[len(content):]
            content = content.rstrip()
            final_lines.append(content + ending)
         else:
            final_lines.append(line.rstrip())
    return "".join(final_lines)

def remove_comments(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.py':
        modified = remove_python_comments(source)
    elif ext in ['.c', '.cpp', '.h', '.hpp', '.java', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.kt', '.swift', '.php', '.cs']:
        modified = remove_c_style_comments(source)
    elif ext in ['.sh', '.yaml', '.yml', '.rb', '.pl']:
        modified = remove_hash_comments(source)
    else:
        return None

    return modified

def main():
    parser = argparse.ArgumentParser(description="Remove inline comments from code files.")
    parser.add_argument("filenames", nargs="+", help="Files to process")
    args = parser.parse_args()

    ret_code = 0
    for filename in args.filenames:
        try:
            modified = remove_comments(filename)
            
            if modified is not None:
                with open(filename, 'r', encoding='utf-8') as f:
                    original = f.read()
                
                if modified != original:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(modified)
                    print(f"Removed comments from {filename}")
                    ret_code = 1
        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
    
    return ret_code

if __name__ == "__main__":
    sys.exit(main())