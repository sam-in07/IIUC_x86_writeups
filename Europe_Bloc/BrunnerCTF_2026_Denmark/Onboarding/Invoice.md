```markdown
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/forensics_invoice]
└─$ olevba "Invoice #1337.docm"

olevba 0.60.2 on Python 3.13.12 - http://decalage.info/python/oletools
===============================================================================
FILE: Invoice #1337.docm
Type: OpenXML
WARNING  For now, VBA stomping cannot be detected for files in memory
-------------------------------------------------------------------------------
VBA MACRO ThisDocument.cls 
in file: word/vbaProject.bin - OLE stream: 'VBA/ThisDocument'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Private Sub Document_open()

    Dim flag
    flag = "brunner{" & "1_w0nt_p4y_th3m_4_d1me}"
    Dim wsh As Object
    Set wsh = VBA.CreateObject("WScript.Shell")
    Dim waitOnReturn As Boolean: waitOnReturn = True
    Dim windowStyle As Integer: windowStyle = 1
    
    wsh.Run "cmd.exe /S /C echo " & flag, windowStyle, waitOnReturn

End Sub
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|AutoExec  |Document_open       |Runs when the Word or Publisher document is  |
|          |                    |opened                                       |
|Suspicious|Shell               |May run an executable file or a system       |
|          |                    |command                                      |
|Suspicious|WScript.Shell       |May run an executable file or a system       |
|          |                    |command                                      |
|Suspicious|Run                 |May run an executable file or a system       |
|          |                    |command                                      |
|Suspicious|CreateObject        |May create an OLE object                     |
|IOC       |cmd.exe             |Executable file name                         |
+----------+--------------------+---------------------------------------------+

```
                                                                                                                                                            
## flag = "brunner{1_w0nt_p4y_th3m_4_d1me}"