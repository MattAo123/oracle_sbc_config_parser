# Importing librares

import json

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


show_test = '''certificate-record
        name                                    Mgmt
        country                                 IT
        state                                   Milan
        locality                                Milan
        organization                            Test SBC
        unit                                    Test SBC
        common-name                             test_sbc.local
        extended-key-usage-list                 serverAuth
                                                clientAuth
codec-policy
        name                                    OnlyG711
        allow-codecs                            PCMA PCMU telephone-event
filter-config
        name                                    AllTraffic
        user                                    sip
http-server
        name                                    MGMT
        http-state                              disabled
        https-state                             enabled
        tls-profile                             HTTPS
local-policy
        from-address                            *
        to-address                              *
        source-realm                            Inside
        policy-attribute
                next-hop                                lrt:Outside
        policy-attribute
                next-hop                                lrt:ToCUCM
local-routing-config
        name                                    Outside
        file-name                               Outside.xml.gz
media-manager
network-interface
        name                                    Inside
        hostname                                inside.local.com
        ip-address                              1.1.1.1
        netmask                                 255.255.255.0
        gateway                                 1.1.1.2
        dns-ip-primary                          8.8.8.8
        dns-ip-backup1                          8.8.4.4
        dns-ip-backup2                          172.16.0.191
network-interface
        name                                    Outside
        hostname                                outside.local.com
        ip-address                              4.4.4.4
        netmask                                 255.255.255.0
        gateway                                 4.4.4.2
        dns-ip-primary                          8.8.8.8
        dns-ip-backup1                          8.8.4.4
ntp-config
        server                                  10.10.10.10
                                                20.20.20.20
phy-interface
        name                                    Inside
        operation-type                          Media
phy-interface
        name                                    Outside
        operation-type                          Media
        slot                                    1
realm-config
        identifier                              Outside
        description                             Realm for connections to Provider
        network-interfaces                      Outside:0.4
        qos-enable                              enabled
        codec-policy                            OnlyG711
realm-config
        identifier                              Inside
        description                             Realm for connections to CUCM Cluster
        network-interfaces                      Inside:0.4
        qos-enable                              enabled
session-agent
        hostname                                cucm.local.com
        ip-address                              1.1.1.3
        state                                   disabled
        realm-id                                Inside
        description                             CUCM
        ping-method                             OPTIONS;hops=0
        ping-interval                           30
        options                                 ping-failure-count=3
session-agent
        hostname                                cucm02.local.com
        ip-address                              1.1.1.4
        state                                   disabled
        realm-id                                Inside
        description                             CUCM2
        ping-method                             OPTIONS;hops=0
        ping-interval                           30
        options                                 ping-failure-count=3
session-agent
        hostname                                provider.local.com
        ip-address                              4.4.4.3
        state                                   disabled
        realm-id                                Outside
        description                             Provider
        ping-method                             OPTIONS;hops=0
        ping-interval                           30
        options                                 ping-failure-count=3
session-group
        group-name                              provider
        strategy                                RoundRobin
        dest                                    provider.local.com
        sag-recursion                           enabled
        stop-sag-recurse                        400-407,409-499
session-group
        group-name                              CUCM-Ita
        strategy                                RoundRobin
        dest                                    cucm.local.com
                                                cucm02.local.com
        sag-recursion                           enabled
        stop-sag-recurse                        400-407,409-499
sip-config
        dialog-transparency                     disabled
        options                                 egress-realm-param=outrealm
                                                max-udp-length=0
        sip-message-len                         10000
        enum-sag-match                          enabled
sip-interface
        realm-id                                Outside
        description                             Sip Interface for connections to Provider
        sip-port
                address                                 4.4.4.1
                allow-anonymous                         agents-only
sip-interface
        realm-id                                Inside
        sip-port
                address                                 1.1.1.1
                transport-protocol                      TCP
                allow-anonymous                         agents-only
sip-manipulation
        name                                    IN_TEST
        description                             test
        header-rule
                name                                    Modify_Pai
                header-name                             P-Asserted-Identity
                action                                  manipulate
                comparison-type                         pattern-rule
                msg-type                                request
                methods                                 INVITE
                element-rule
                        name                                    modify_uriuser
                        type                                    uri-user
                        action                                  replace
                        comparison-type                         pattern-rule
                        match-value                             ^00(.*)$
                        new-value                               "+"+$1
        header-rule
                name                                    Modify_From
                header-name                             From
                action                                  manipulate
                comparison-type                         pattern-rule
                msg-type                                request
                methods                                 INVITE
                element-rule
                        name                                    modify_uriuser
                        type                                    uri-user
                        action                                  replace
                        comparison-type                         pattern-rule
                        match-value                             ^00(.*)$
                        new-value                               "+"+$1
        header-rule
                name                                    Modify_RPID
                header-name                             Remote-Party-ID
                action                                  manipulate
                comparison-type                         pattern-rule
                msg-type                                request
                methods                                 INVITE
                element-rule
                        name                                    modify_uriuser
                        type                                    uri-user
                        action                                  replace
                        comparison-type                         pattern-rule
                        match-value                             ^00(.*)$
                        new-value                               "+"+$1
        header-rule
                name                                    Modify_RURI
                header-name                             Request-Uri
                action                                  manipulate
                comparison-type                         pattern-rule
                msg-type                                request
                methods                                 INVITE
                element-rule
                        name                                    modify_uriuser_00
                        type                                    uri-user
                        action                                  replace
                        comparison-type                         pattern-rule
                        match-value                             ^00(.*)$
                        new-value                               "+"+$1
        header-rule
                name                                    Modify_To
                header-name                             To
                action                                  manipulate
                comparison-type                         pattern-rule
                msg-type                                request
                methods                                 INVITE
                element-rule
                        name                                    modify_uriuser_00
                        type                                    uri-user
                        action                                  replace
                        comparison-type                         pattern-rule
                        match-value                             ^00(.*)$
                        new-value                               "+"+$1
sip-monitoring
        monitoring-filters                      AllTraffic
system-config
        comm-monitor
                state                                   enabled
                interim-qos-update                      enabled
                monitor-collector
                        address                                 3.3.3.3
        default-gateway                         1.1.1.2
        telnet-timeout                          1800
tls-profile
        name                                    HTTPS
        end-entity-certificate                  Mgmt'''


conf = show_run_parser(show_test)
print(json.dumps(conf,indent=2))