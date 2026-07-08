definitely the oldest trick in the book
nc 15.235.202.47 8999 

┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ chmod +x chall       
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ ./chall     
Let me know the length of your buffer: 
^Z
zsh: suspended  ./chall
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ ltrace ./chall                
setvbuf(0x7fe8d416b5c0, nil, 2, 0)                                                              = 0
setvbuf(0x7fe8d416a8e0, nil, 2, 0)                                                              = 0
puts("Let me know the length of your b"...Let me know the length of your buffer: 
)                                                     = 40
__isoc99_scanf(0x402030, 0x7ffd176b2d7c, 0x7fe8d416c790, 0x7fe8d416c790^Z
zsh: suspended  ltrace ./chall
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ ./chall
Let me know the length of your buffer: 
1024
So u want to overflow this challenge??
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ ./chall 
Let me know the length of your buffer: 
8
okay, so your length is 8
> 
AAAAAAAABBBBBBBBCCCCCCCC
Let's me check if you are safe or not!
You doing it right. Are you?
Your overflow attempt is 999999
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ BBBBBBBBCCCCCCCC
BBBBBBBBCCCCCCCC: command not found
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ checksec ./chall
Error: No option selected. Please select an option.

                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ objdump -d -M intel ./chall | less
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles]
└─$ strings ./chall
/lib64/ld-linux-x86-64.so.2
setvbuf
stdin
puts
read
getchar
stdout
__libc_start_main
printf
__isoc99_scanf
libc.so.6
GLIBC_2.7
GLIBC_2.2.5
GLIBC_2.34
__gmon_start__
PTE1
H=@@@
LYKNCTF{H
this_is_H
a_super_H
fake_flaH
e_flag_fH
or_you}
Let me know the length of your buffer: 
So u want to overflow this challenge??


LYKNCTF{Hthis_is_Ha_super_Hfake_flaHe_flag_for_you}


LYKNCTF{_c4nhi3u_}