org 100h

jmp start

infile  db 'input.txt',0
outfile db 'output.hfc',0

buffer  db 200 dup(0)
buffer2 db 400 dup(0)

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

; RLE COMPRESSION
mov si,buffer
mov di,buffer2

next_char:
cmp si,bp
jae done_rle

mov al,[si]
mov bl,al
mov cx,1

count_loop:
inc si
cmp si,bp
jae write_pair
mov al,[si]
cmp al,bl
jne write_pair
inc cx
jmp count_loop

write_pair:
mov ax,cx

emit_nines:
cmp ax,9
jbe emit_last
mov byte [di],'9'
inc di
mov [di],bl
inc di
sub ax,9
jmp emit_nines

emit_last:
add al,'0'
mov [di],al
inc di
mov [di],bl
inc di
jmp next_char

done_rle:
; CREATE OUTPUT FILE
mov ah,3Ch
xor cx,cx
mov dx,outfile
int 21h
jc create_error
mov bx,ax

; WRITE COMPRESSED DATA
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