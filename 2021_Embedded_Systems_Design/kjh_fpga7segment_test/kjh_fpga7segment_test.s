	.arch armv7-a
	.fpu softvfp
	.eabi_attribute 20, 1
	.eabi_attribute 21, 1
	.eabi_attribute 23, 3
	.eabi_attribute 24, 1
	.eabi_attribute 25, 1
	.eabi_attribute 26, 2
	.eabi_attribute 30, 2
	.eabi_attribute 34, 1
	.eabi_attribute 18, 4
	.file	"kjh_fpga7segment_test.c"
	.section	.text.startup,"ax",%progbits
	.align	2
	.global	main
	.type	main, %function
main:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, r5, r6, lr}
	cmp	r0, #1
	sub	sp, sp, #8
	mov	r6, #0
	mov	r4, r1
	strh	r6, [sp, #4]	@ movhi
	ble	.L6
	ldr	r0, .L7
	mov	r1, #1
.LPIC1:
	add	r0, pc, r0
	bl	open(PLT)
	cmn	r0, #1
	mov	r5, r0
	beq	.L4
	ldr	r0, [r4, #4]
	bl	atoi(PLT)
	uxtb	r4, r0
	ldr	r0, .L7+4
	mov	r1, r4
	mov	r2, r4
.LPIC2:
	add	r0, pc, r0
	bl	printf(PLT)
	add	r1, sp, #4
	mov	r2, #2
	mov	r0, r5
	mov	r3, r4, lsr #4
	and	r4, r4, #15
	strb	r3, [sp, #4]
	strb	r4, [sp, #5]
	bl	write(PLT)
	movw	r0, #3000
	bl	sleep(PLT)
	mov	r0, r5
	bl	close(PLT)
	mov	r0, r6
.L3:
	add	sp, sp, #8
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, pc}
.L4:
	ldr	r0, .L7+8
.LPIC3:
	add	r0, pc, r0
	bl	puts(PLT)
	mov	r0, r5
	b	.L3
.L6:
	ldr	r0, .L7+12
.LPIC0:
	add	r0, pc, r0
	bl	puts(PLT)
	mvn	r0, #0
	b	.L3
.L8:
	.align	2
.L7:
	.word	.LC1-(.LPIC1+8)
	.word	.LC2-(.LPIC2+8)
	.word	.LC3-(.LPIC3+8)
	.word	.LC0-(.LPIC0+8)
	.size	main, .-main
	.section	.rodata.str1.4,"aMS",%progbits,1
	.align	2
.LC0:
	.ascii	"please input the parameter! ex)./test 0 ~ 255\000"
	.space	2
.LC1:
	.ascii	"/dev/kjh_fpga7segment\000"
	.space	2
.LC2:
	.ascii	"value : %d, %X \012\000"
	.space	3
.LC3:
	.ascii	"Device Open error!\000"
	.ident	"GCC: (GNU) 4.8"
	.section	.note.GNU-stack,"",%progbits
