import os
import markdown
from pathlib import Path
import pdoc

# Generate the documentation
pdoc.render.configure(
    docformat='numpy',
    include_undocumented=False
)
pdoc.pdoc('listeningpy', output_directory=Path('docs'))


# Assume path_to_docs is the directory where pdoc outputs its HTML files
path_to_docs = Path('./docs')

# Assume examples_folder is the directory where your markdown example files are located
examples_folder = './examples'

# Get a list of all markdown files in the examples folder
example_files = [f for f in os.listdir(examples_folder) if f.endswith('.md')]

# Convert the files to HTML
html_docs = []
for file in example_files:
    with open(os.path.join(examples_folder, file), 'r') as f:
        markdown_content = f.read()
        html_content = markdown.markdown(markdown_content)
        # Wrap the content in the pdoc HTML structure
        html_content = f'<div class="pdoc">{html_content}</div>'
        html_docs.append(html_content)

# Create separate HTML files for each example
for i, html_doc in enumerate(html_docs):
    example_name = example_files[i].replace('.md', '')
    example_path = path_to_docs / 'examples' / f'{example_name}.html'
    with open(example_path, 'w') as f:
        f.write(html_doc)

# Add the HTML file links to the main HTML file
html_file_path = path_to_docs / 'listeningpy.html'

with open(html_file_path, 'r') as f:
    html_content = f.read()

# Find the position of the first </ul> tag after <h2>Submodules</h2> in the HTML content
submodules_position = html_content.find('</ul>', html_content.find('<h2>Submodules</h2>'))

# Create the new menu section for Examples
new_menu_section = '\n<h2>Examples</h2>\n<ul>'
for file in example_files:
    example_name = file.replace('.md', '')
    new_menu_section += f'\n    <li><a href="examples/{example_name}.html">{example_name}</a></li>'
new_menu_section += '\n</ul>'

# Find the position of the first </ul> tag after <h2>Submodules</h2> in the HTML content
submodules_position = html_content.find('</ul>', html_content.find('<h2>Submodules</h2>'))

# Insert the new menu section after the </ul> tag
html_content = html_content[:submodules_position+5] + new_menu_section + html_content[submodules_position+5:]

# Save the changes to the HTML file
with open(html_file_path, 'w') as f:
    f.write(html_content)