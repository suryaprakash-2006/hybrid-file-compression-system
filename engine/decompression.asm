org 100h

jmp start

infile  db 'input.txt',0
outfile db 'output.txt',0

buffer  db 200 dup(0)
buffer2 db 1200 dup(0)

msg1 db 'Cannot open input file$'
msg2 db 'Cannot create output file$'

start:
push cs
pop ds

; OPEN INPUT FILE
mov ah,3Dh
xor al,al
mov dx,infile
int 21h
jc open_error
mov bx,ax

; READ FILE
mov ah,3Fh
mov cx,200
mov dx,buffer
int 21h
mov bp,ax
add bp,buffer

; CLOSE INPUT FILE
mov ah,3Eh
int 21h

; RLE DECOMPRESSION
mov si,buffer
mov di,buffer2

next_token:
cmp si,bp
jae done_rle

xor cx,cx

read_digits:
cmp si,bp
jae done_rle

mov al,[si]
cmp al,'0'
jb got_char
cmp al,'9'
ja got_char

sub al,'0'
mov ah,0

push ax
mov ax,cx
mov bx,10
mul bx
mov cx,ax
pop ax

add cx,ax
inc si
jmp read_digits

got_char:
cmp cx,0
je skip_char
mov al,[si]

write_repeat:
mov [di],al
inc di
loop write_repeat

skip_char:
inc si
jmp next_token

done_rle:
; CREATE OUTPUT FILE
mov ah,3Ch
xor cx,cx
mov dx,outfile
int 21h
jc create_error
mov bx,ax

; WRITE DECOMPRESSED DATA
mov ah,40h
mov cx,di
sub cx,buffer2
mov dx,buffer2
int 21h

; CLOSE OUTPUT FILE
mov ah,3Eh
int 21h

exit:
mov ax,4C00h
int 21h

open_error:
mov ah,09h
mov dx,msg1
int 21h
jmp exit

create_error:
mov ah,09h
mov dx,msg2
int 21h
jmp exit
