org 100h

.data

infile  db 'input.txt',0
outfile db 'output.hfc',0

buffer  db 200 dup(?)    
buffer2 db 200 dup(?)     

msg1 db 'Cannot open input file$',0
msg2 db 'Cannot create output file$',0

.code

start:


mov ax,@data
mov ds,ax


; OPEN INPUT FILE

mov ah,3Dh
mov al,0
mov dx,offset infile
int 21h
jc open_error

mov bx,ax         


; READ FILE

mov ah,3Fh
mov cx,200
mov dx,offset buffer
int 21h

mov bp,ax          

; close input file
mov ah,3Eh
int 21h


; RLE COMPRESSION

lea si,buffer
lea di,buffer2

next_char:

mov al,[si]
cmp si,offset buffer + 200
je done_rle

mov bl,al
mov cx,1

count_loop:

inc si
cmp si,offset buffer + 200
je write_pair

mov al,[si]
cmp al,bl
jne write_pair

inc cx
jmp count_loop


write_pair:

mov dl,cl
add dl,'0'
mov [di],dl
inc di

mov [di],bl
inc di

jmp next_char


done_rle:

; CREATE OUTPUT FILE

mov ah,3Ch
mov cx,0
mov dx,offset outfile
int 21h
jc create_error

mov bx,ax           ; output handle


; WRITE COMPRESSED DATA

mov ah,40h
mov cx,di
sub cx,offset buffer2
mov dx,offset buffer2
int 21h

; close output file
mov ah,3Eh
int 21h

; exit program
mov ah,4Ch
int 21h



; ERROR HANDLING

open_error:
mov ah,09h
mov dx,offset msg1
int 21h
jmp exit

create_error:
mov ah,09h
mov dx,offset msg2
int 21h

exit:
mov ah,4Ch
int 21h