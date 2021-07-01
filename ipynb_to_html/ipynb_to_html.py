##########
#Imports
##########


import sys
import getopt
import os
import json
import markdown


##########
#Manual
##########


manual = """NAME
ipynb_to_html.py - convert jupyter notebooks to simple html files

SYNOPSIS
ipynb_to_html.py [-i <inputfile>] [-s <stylesheet>] [-n]

EXAMPLES
ipynb_to_html.py -i example.ipynb -s default.css
ipynb_to_html.py -i example -s default -n

DESCRIPTION

[-i <inputfile>]
mandatory. <inputfile> will be looked for in the ipynb directory.
<inputfile> must be of type ipynb.

[-s <stylesheet>]
optional. <stylesheet> will be looked for in the styles directory.
<stylesheet> must be of type css.
Default value : default.css

[-n]
optional : no inputs.
If set, source for the code cells will not be rendered.
Default value : False"""


##########
#File variables
##########


file_name = ''
input_path = ''
output_path = ''
style = 'default'
style_path = 'styles/default.css'
missing_input = True
no_inputs = False


##########
#Command line arguments
##########


try:
    opts, args = getopt.getopt(sys.argv[1:], 'hi:s:n')
except getopt.GetoptError:
    print('Incorrect arguments \nPlease use ipynb_to_html.py -h for help')
    sys.exit(2)


for opt, arg in opts:
    #print manual
    if opt == '-h':
        print(manual)
    #input, output
    elif opt == '-i':
        file_name = os.path.splitext(arg)[0]
        input_path = ''.join(['ipynb/',file_name,'.ipynb'])
        if not os.path.isfile(input_path):
            print('Input file not found \nPlease use ipynb_to_html.py -h for help')
            sys.exit(2)
        output_path = ''.join(['html/',file_name,'.html'])
        missing_input = False
    #style
    elif opt == '-s':
        style = os.path.splitext(arg)[0]
        style_path = ''.join(['styles/',style,'.css'])
        if not os.path.isfile(style_path):
            print('Style file not found \nPlease use ipynb_to_html.py -h for help')
            sys.exit(2)
    #no inputs
    elif opt == '-n':
        no_inputs = True

#input is mandatory
if missing_input:
    print('Missing input file \nPlease use ipynb_to_html.py -h for help')


##########
#Fetch style contents
##########


with open(style_path, 'r') as open_file:
    style_contents = open_file.read()


##########
#Output file initialization
##########


to_write = """<!doctype html>

<html>


<head>

<title>"""+file_name+"""</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

<style type="text/css">
"""+style_contents+"""</style>

</head>


<body>"""

with open(output_path, 'w') as open_file:
    open_file.write(to_write)


##########
#Fetch notebook contents
##########


with open(input_path, 'r') as open_file:
    notebook_contents = json.load(open_file)


##########
#Main loop
##########


number_of_cells = len(notebook_contents['cells'])

for i in range(number_of_cells):
    current_cell = notebook_contents['cells'][i]
    
    #markdown cell
    if current_cell['cell_type'] == 'markdown':
        to_write = '\n\n<div class="markdown">\n'
        to_write += markdown.markdown(''.join(current_cell['source']))
        to_write += '\n</div>'
        with open(output_path, 'a') as open_file:
            open_file.write(to_write)
    #raw cell
    elif current_cell['cell_type'] == 'raw':
        to_write = '\n\n<div class="raw">\n<pre>'
        to_write += ''.join(current_cell['source']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        to_write += '</pre>\n</div>'
        with open(output_path, 'a') as open_file:
            open_file.write(to_write)

    #code cell
    elif current_cell['cell_type'] == 'code':
        to_write = '\n\n<div class="code">'
        #input
        if not no_inputs:
            if current_cell['execution_count'] is not None:
                to_write += '\nInput['+str(current_cell['execution_count'])+']'
            to_write += '\n<div class="source">\n<pre>'
            to_write += ''.join(current_cell['source']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            to_write += '</pre>\n</div>'
        #output(s)
        if len(current_cell['outputs']) > 0:
            if current_cell['execution_count'] is not None:
                to_write += '\nOutput['+str(current_cell['execution_count'])+']'
            for j in range(len(current_cell['outputs'])):
                current_output = current_cell['outputs'][j]
                #output types
                #stream (text output to stdout)
                if current_output['output_type'] == 'stream':
                    to_write += '\n<div class="stream">\n<pre>'            
                    to_write += ''.join(current_output['text']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    to_write += '</pre>\n</div>'
                #display_data (graphical output eg matplotlib)
                if current_output['output_type'] == 'display_data':
                    to_write += '\n<div class="display_data">\n'
                    to_write += '<img src="data:image/png;base64,'+current_output['data']['image/png'][:-1]+'" />'
                    to_write += '\n</div>'
                #execute_result (tabular or text data eg pandas) : using text version
                if current_output['output_type'] == 'execute_result':
                    to_write += '\n<div class="execute_result">\n<pre>' 
                    to_write += ''.join(current_output['data']['text/plain']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    to_write += '</pre>\n</div>'

        to_write += '\n</div>'
        with open(output_path, 'a') as open_file:
            open_file.write(to_write)


##########
#Output file - close tags
##########


to_write = """

</body>


</html>"""

with open(output_path, 'a') as open_file:
    open_file.write(to_write)


##########
#Debug prints
##########


print("File name : ", file_name)
print("Input file path : ", input_path)
print("Output file path : ", output_path)
print("Style : ", style)
print("Style path : ", style_path)
print("Number of cells : ", number_of_cells)
