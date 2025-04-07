# Importing librares

import json
from netmiko import ConnectHandler

# Function that parse a show run, or show run short of an Oracle SBC, and return a dictionary with all the values.
def show_run_parser(show):
    
    # Dictionary to store the data
    parsed_data = {}
    
    # Stack to track the context (dictionary, indentation level)
    stack = [(parsed_data, -1)] 
    
    # Used to keeps track of the previous command and previous value to handle lists
    prev_command = None  
    value_indent = None
    
    # Creating a list with all the lines of the variable
    lines = show.splitlines()
    
    # Cicle for every single line
    for line in lines:
        
        # Count leading spaces to track the indent level of the command
        indent_level = len(line) - len(line.lstrip()) 
        # Strips all the spaces, to have a clean command-value
        clean_line = line.strip()

        # Ignores empty lines if any
        if not clean_line:
            continue 
        
        # split command, value
        parts = clean_line.split(maxsplit=1)
        
        # Command of the line
        command = parts[0]
        
        # If no value present in parts[1] value remains none
        value = parts[1] if len(parts) > 1 else None

        # command value example:
        #     session-group                     --> parts[0]: session-group - parts[1]: None
        #             group-name        test_sg --> parts[0]: group-name - parts[1]: test_sg
        #             dest              1.1.1.1 --> parts[0]: dest - parts[1]: 1.1.1.1
        #                               2.2.2.2 --> parts[0]: 2.2.2.2 - parts[1]: None
        #                                       This above is the only exception, when a command variable
        #                                       instead of be a command, is the actual value of the command
                
        
        # If value is present, tracks the indent of the command
        if value:
            value_indent = len(line) - len(line.replace(command,' ' * len(command)).lstrip())
        
        # Find the exact right indent in the stack
        while stack and stack[-1][1] >= indent_level:
            stack.pop()

        # Loading the dictionary based on the indent level of the command
        parent_dict = stack[-1][0]

        # if the command is already present and it's a dictionary, transform it in a list and insert the already converted conf
        if command in parent_dict and isinstance(parent_dict[command], dict):
            parent_dict[command] = [parent_dict[command]]
            
        # If is already a list
        if command in parent_dict and isinstance(parent_dict[command], list):
            
            # If value is none, create a new empty dictionary, if not new_dict = value
            new_dict = {} if not value else value
            # Append the new dictionary inside the command list
            parent_dict[command].append(new_dict)
            
            # If new dict is a dictionary, create a new element in the stack variable with dictionary and indent level
            if isinstance(new_dict, dict):
                stack.append((new_dict, indent_level))
        
        # If command is not in the dictionary, this is the first time we encounter it
        else:
            # If value contains something, the dictionary is populated with command as key, and it value as dict value
            if value:
                parent_dict[command] = value
                
                # Keep tracks of the command in prev_command variable to handle multiline commands
                prev_command = command 
                
            # if value is empty it means that is a new command, or a new value of a single command like options or dest for a session-group
            # try to see if the line above was a command (value indent is not None), if the indent level of actual command is different than value_indent, this is a sub-element of the config
            # and for that create a new dictionary, insert in the parent dictionary, and append it to the stack
            elif (value_indent and indent_level != value_indent) or not value_indent:
                new_dict = {}
                parent_dict[command] = new_dict
                stack.append((new_dict, indent_level))
                
                # Reset previous keys with the command, and value_indent to None
                prev_command = command 
                value_indent = None

        # Instead, if value is none (only 1 element on this line) and prev_command is already present, and value_indent is filled
        # This is a new value for the same command, like options or dest for session-group
        
        if value is None and prev_command in parent_dict and value_indent:
            
            # if parent_dict of this command it already a list, append the new value
            if isinstance(parent_dict[prev_command], list):
                parent_dict[prev_command].append(command)  # Aggiungi alla lista esistente
            
            # If not transform it to a list and insert the values.
            else:
                parent_dict[prev_command] = [parent_dict[prev_command], command]  # Converti in lista e aggiungi elemento

    # At the end return the whole show run parsed and transformed in a dictionary
    return parsed_data

ip = '1.1.1.1'
username = 'admin'
password = 'password123'
device ={
    "device_type": "linux",
    "host" : ip,
    "username" : username,
    "password" : password,
    "port" : 22
}

try:
    cli = ConnectHandler(**device)

except Exception as e:
    print('issue with the connection: ' +e)

print(f"Connected ")

show_test = cli.send_command("show running-config tls-profile short")
# show_test = cli.send_command("show running-config short")
# show_test = cli.send_command("show running-config session-group short")

cli.disconnect()

conf = show_run_parser(show_test)
print(json.dumps(conf,indent=2))