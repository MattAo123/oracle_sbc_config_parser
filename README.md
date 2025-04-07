# Oracle SBC Config Parser

Python function to parse and transform Oracle SBCs configuration in a dictionary.

### Requirements

This script tested on W11 Powershell with Python 3.12.9
Packages required are in requirements.txt

It's recommended to crate a virtual environment, activate it and then install the packages:

```sh
$ python3 -m venv ./VENV-NAME
$ .\VENV-NAME\Scripts\Activate.ps1
$ pip install -r requirements.txt
```

>NOTE: chose a name for virtual environment and replace the `VENV-NAME` string

### How it works

The script 'simple_parser.py' transforms a show run of an Oracle SBC pasted in the show_test variable and return a dictionary, printing it with indentation

The script 'parser_with_netmiko.py' let you insert SBC details (ip, username, password), connect to it and save the 'show run' command in a variable and the parse it.

### How to use it

#### simple_parser.py
Open the py file, edit the show_test variable putting the output you wanna parse.
>NOTE: use triple ' when creating the variable, to keep all the indentation!
```python
---
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
---
```

and run the script.

#### parser_with_netmiko.py
Open the py file, edit the ip, username, password variables and change the command sent to the CLI based on your needs

```python
---
ip = '1.1.1.1'
username = 'admin'
password = 'password123'
show_test = cli.send_command("show running-config tls-profile short")
---
```

and run the script.

# MIT License
Feel free to edit, improve and share.
