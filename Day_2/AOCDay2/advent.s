//
//  advent.s
//  AdventOfCode2022Test
//
//  Created by Badger on 27/11/2023.
//

.data
myString:
    .asciz "Input string was: %s\n"


.text
.global _foo

// callee-save registers (%rsp, %rbx, %rbp, or %r12-r15)



// void foo(char**, size_t)
_foo:
    // Preserve the frame pointer
    pushq %rbp
    // Set the frame pointer to our frame
    movq %rsp, %rbp

    // Allocate room on the stack for local var
    // subq $0x18, %rsp

    // Preserve callee-saved registers that we're going to use
    pushq %rbx
    pushq %r12
    pushq %r13

    // Preserve caller saved registers
    push %r10
    push %r11
    push %rdi

    // Move parameter
    movq $69, %rdi
    call _from_asm
    
    // N.B. Return value in in RAX

    // Restore caller saved registers
    pop %rdi
    pop %r11
    pop %r10

    // Attempt to call printf with one of the values passed to us
    // Preserve caller saved registers
    push %r10
    push %r11
    push %rdi

    // Get the second pointer
    movq %rdi, %rax
    addq $8, %rax
    movq (%rax), %rsi

    //movq $myString, %rdi
    // TODO: Doc why this didn't work
    lea myString(%rip), %rdi
    
    //movl $10, %esi
    
    call _printf
    // N.B. Return value in in RAX

    // Restore caller saved registers
    pop %rdi
    pop %r11
    pop %r10
    
    // Clean up our local vars
    // addq $0x18, %rsp

    // Restore callee-saved registers
    popq %r13
    popq %r12
    popq %rbx

    // Reset the stack pointer and base pointer
    movq %rbp, %rsp
    popq %rbp

    // Return to caller. N.B. This basically will change the instruction
    // pointer RIP to a value located on the stack.
    ret
