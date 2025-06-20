# Wazuh Active Response: AppLocker Monitor

## Doel

Testen hoe we effectief een eigen `active-response` kunnen configureren binnen Wazuh, specifiek gericht op AppLocker-detectie (zoals EventID 8004). Deze setup maakt het mogelijk alerts te loggen, te dumpen, en automatisch te verwerken.

---

## 🧱 Stap 1: Configureer de Wazuh-server

### 1.1 Voeg een custom command toe aan `ossec.conf`

Plaats het volgende blok bij andere `<command>` entries:

```
<command>
  <name>wazuh-applocker</name>
  <executable>wazuh-applocker.exe</executable>
  <timeout_allowed>no</timeout_allowed>
</command>
```

### 1.2 Voeg een active-response toe

Plaats het volgende blok binnen '<active-response>':

```
<active-response>
  <disabled>no</disabled>
  <command>wazuh-applocker</command>
  <location>local</location>
  <rules_id>100000</rules_id>
</active-response>
```

# 🧩 Stap 2: Configureer de Wazuh-agent

Pas het configuratiebestand aan op de agent:

```
C:\Program Files (x86)\ossec-agent\local_internal_options.conf
```

Voeg deze regels toe:
```
wazuh_command.remote_commands=1
logcollector.remote_commands=1
```

Herstart daarna de Wazuh-agent.

# Stap 3: Python-script voor Active Response

Download het volgende script op als wazuh-applocker.py

# Stap 4: Compileer naar .exe

Gebruik pyinstaller:
```
python -m PyInstaller --clean --onefile wazuh-applocker.py
```
Kopieer de .exe naar:
```
C:\Program Files (x86)\ossec-agent\active-response\bin\
```

# Stap 5: Test/Trigger je active-response

1. Herstart de Wazuh-agent op de target host.
2. Trigger een alert (bijv. met whoami.exe of PowerShell).
3. Controleer:
- alert-dump.json → volledige alert dump
- parsed-dump.json → gevlakte keys
- active-responses.log → logs met resultaten en errors/debugs

!Zie je geen output? Restart de agent handmatig opnieuw.

## Voorbeeld output
```
2025/06/20 15:36:26 wazuh-applocker.exe: [INFO] AppLocker AR started  
2025/06/20 15:37:02 wazuh-applocker.exe: [DEBUG] Extracted: version=1, origin.name=node01, command=add, parameters.command=add, parameters.alert.id=1750427242.11682046 ...
2025/06/20 15:37:02 wazuh-applocker.exe: [INFO] AppLocker AR completed
```
