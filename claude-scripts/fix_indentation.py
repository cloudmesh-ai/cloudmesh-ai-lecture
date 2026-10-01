import sys, os, glob

files = glob.glob("docs/new/vm/*-chapter.md")
for file_path in files:
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("!!!") or line.startswith("???"):
            new_lines.append(line)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() == "":
                    new_lines.append(next_line)
                elif next_line.startswith("!!!") or next_line.startswith("???"):
                    break
                else:
                    if not next_line.startswith("    "):
                        new_lines.append("    " + next_line)
                    else:
                        new_lines.append(next_line)
                i += 1
            continue
        else:
            new_lines.append(line)
        i += 1

    with open(file_path, "w") as f:
        f.writelines(new_lines)
