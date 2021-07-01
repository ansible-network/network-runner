import json
from network_runner import exceptions


def format_port_config(data, os):
    """Use standard format json string replace port configuration string

    :param data: The output of ansible play command
    :type data: String
    :param os: The system of the switch
    :type os: String

    :returns: String
    """
    # find source port configuration json string
    source_config_json = ''
    count = 0
    for char in data:
        if char == '{':
            count += 1
            # begin of json string
            if count == 1:
                source_config_json = ''
        elif char == '}':
            count -= 1
            # end of json string
            if count == 0:
                source_config_json = source_config_json + '}'
        if count > 0:
            source_config_json += char
    if count != 0:
        raise exceptions.NetworkRunnerException(
            'invaild json format: '.join(source_config_json))
    # transform source port configuration to target port configuration
    source_config = json.loads(source_config_json.replace('\n', ' '))
    target_config = {
        'mode': None,
        'vlan': None,
        # format 1-12,15,17-20
        'trunked_vlans': '',
    }
    if os == "fos":
        lines = source_config['stdout_lines'][0]
        for line in lines:
            # deal switchport mode
            if line.startswith('switchport mode '):
                target_config['mode'] = line.replace(
                    'switchport mode ', '')
            # deal vlan
            if line.startswith('switchport access vlan '):
                target_config['vlan'] = int(line.replace(
                    'switchport access vlan ', ''))
            # deal trunked vlans
            if line.startswith('switchport trunk allowed vlan '):
                target_config['trunked_vlans'] = line.replace(
                    'switchport trunk allowed vlan ', '')
    else:
        raise exceptions.NetworkRunnerException('invaild os type')
    # replace source port configuration json to target port configuration json
    return data.replace(source_config_json, json.dumps(target_config))
