┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/public/emails]

└─$ ls 

sample-1000.eml  sample-1014.eml  sample-189.eml  sample-591.eml  sample-717.eml
sample-1008.eml  sample-1324.eml  sample-405.eml  sample-62.eml   sample-922.eml
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/public/emails]
└─$ grep -Hn "Fatura Emitida" *.eml
sample-717.eml:65:Subject: Fatura Emitida - 6ZFYeMmltso
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/public/emails]
└─$ grep -i "filename=" sample-717.eml
        filename="Vl6s3kCIKaUvwaUAeY.pdf"
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/public/emails]
└─$ 


    Filename: Vl6s3kCIKaUvwaUAeY.pdf

    Subject Identifier: 6ZFYeMmltso

Flag:
grodno{Vl6s3kCIKaUvwaUAeY.pdf_6ZFYeMmltso}