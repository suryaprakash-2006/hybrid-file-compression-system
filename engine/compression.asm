org 100h

.data

input db 'AAAABBBCC$',0
output db 100 dup('$')

.code

start:

mov si, offset input
mov di, offset output

next_char:

mov al, [si]
cmp al, '$'
je finish

mov bl, al
mov cx, 1

count_loop:

inc si
mov al, [si]

cmp al, bl
jne write_output

inc cx
jmp count_loop


write_output:

mov ax, cx
add ax, '0'
mov [di], al
mov [di], bl

inc di
inc di

jmp next_char


finish:

mov [di], '$'

mov ah, 09h
mov dx, offset output
int 21h

mov ah, 4ch
int 21h