## ha_pywinrm

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)


WinRM integration for Home Assistant, using pywinrm

## Usage:

<a href="https://docs.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management" target="_blank">Enable winrm on target device</a>: `winrm qc` 

Add to configuration.yaml using the similar syntax as command_line:

```
switch:
  - platform: ha_pywinrm
    name: [name for this switch]
    host: [IP or hostname]
    username: [username for login]
    password: [password for login]
    command: [command to run]

sensor:
  - platform: ha_pywinrm
    name: [name for this sensor]
    host: [IP or hostname]
    username: [username for login]
    password: [password for login]
    command: [command to run]
    value_template: '{{ value == "0" }}'
  - platform: ha_pywinrm
    name: [name for this sensor]
    host: [IP or hostname]
    username: [username for login]
    password: [password for login]
    command: [command to run]

 binary_sensor:
  - platform: ha_pywinrm
    name: [name for this sensor]
    host: [IP or hostname]
    username: [username for login]
    password: [password for login]
    command: [command to run]

```

Examples:

```
  - platform: ha_pywinrm
    name: File Contents Check
    host: joespc
    password: s00p3rs3kr3t!
    username: joeschmo
    command: 'cat c:\results\output.txt'
    value_template: '{{ value == "success!" }}'
  - platform: ha_pywinrm
    name: Balanced - AC - Monitor Sleep
    host: joespc
    password: s00p3rs3kr3t!
    username: joeschmo
    command: >-
        [CONVERT]::toint16((powercfg /query 381b4222-f694-41f0-9685-ff5bb260df2e 7516b95f-f776-4464-8c53-06167f40cc99 | select-string -Pattern off -Context 0,7)[0].Context.PostContext[-2].split(":")[1].trim(), 16)
    unit_of_measurement: seconds

binary_sensor:
  - platform: ha_pywinrm
    name: Command output validation
    host: 192.168.1.5
    password: s00p3rs3kr3t!
    username: joeschmo
    command: '0,1 | Get-Random'
    payload_on: 1
    payload_off: 0

switch:
  - platform: ha_pywinrm
    switches:
      monitor_sleep:
        friendly_name: Monitor Sleep (1 minute)
        host: 192.168.1.5
        password: s00p3rs3kr3t!
        username: joeschmo
        command_on: 'powercfg -change -monitor-timeout-ac 1'
        command_off: 'powercfg -change -monitor-timeout-ac 0'
        command_state: >-
            [CONVERT]::toint16((powercfg /query 381b4222-f694-41f0-9685-ff5bb260df2e 7516b95f-f776-4464-8c53-06167f40cc99 | select-string -Pattern off -Context 0,7)[0].Context.PostContext[-2].split(":")[1].trim(), 16)
        value_template: '{{ value|int > 0 }}'

```

## Result:

<img style="border: 5px solid #767676;border-radius: 10px;max-width: 350px;width: 100%;box-sizing: border-box;" src="https://github.com/k3wio/ha_pywinrm/blob/master/card.png?raw=true" alt="Card Example">

```
entities:
  - entity: sensor.balanced_ac_monitor_sleep
  - entity: switch.monitor_sleep
  - entity: sensor.file_contents_check
  - entity: binary_sensor.command_output_validation
type: entities
```
