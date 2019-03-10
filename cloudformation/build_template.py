import os

with open('website_monitor.py') as f:
    code_lines = f.readlines()

with open(os.path.join('cloudformation', 'lambda-website-monitor.yaml.tpl')) as f:
    template = f.read()

# TODO: We could probably minify the inline code a bit here, but that involves bringing in more dependencies.

# Don't indent first line
inline_code = code_lines[0]

# Indent all other lines
for code_line in code_lines[1:]:
    if code_line == '\n':  # skip blank lines (sort of minifying)
        continue
    inline_code += '  ' * 5  # 5 indentations of 2 spaces: Resources > Function > Properties > Code > ZipFile > Join
    inline_code += code_line

output = template.replace(
    'raise Exception("Run build_template.py first to load code into CloudFormation template")',
    inline_code
)

with open(os.path.join('cloudformation', 'lambda-website-monitor.yaml'), 'w') as f:
    f.write(output)
