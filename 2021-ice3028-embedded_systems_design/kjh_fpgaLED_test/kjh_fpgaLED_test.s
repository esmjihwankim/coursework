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
	.file	"kjh_fpgaLED_test.c"
	.section	.text.startup,"ax",%progbits
	.align	2
	.global	main
	.type	main, %function
main:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 0, uses_anonymous_args = 0
	ldr	r0, .L7
	mov	r1, #1
	stmfd	sp!, {r4, r5, r6, r7, r8, r9, r10, lr}
.LPIC0:
	add	r0, pc, r0
	sub	sp, sp, #8
	bl	open(PLT)
	ldr	r3, .L7+4
.LPIC2:
	add	r3, pc, r3
	subs	r10, r0, #0
	blt	.L2
	ldr	r2, .L7+8
	add	r9, sp, #4
	ldr	r7, .L7+12
	add	r8, sp, #3
	ldr	r6, .L7+16
	ldr	r4, [r3, r2]
.LPIC3:
	add	r7, pc, r7
.LPIC4:
	add	r6, pc, r6
	add	r5, r4, #84
.L4:
	mov	r3, r5
	mov	r0, r7
	mov	r1, #1
	mov	r2, #26
	bl	fwrite(PLT)
	mov	r1, r6
	mov	r2, r9
	mov	r0, r4
	bl	fscanf(PLT)
	ldr	ip, [sp, #4]
	mov	r0, r10
	mov	r1, r8
	mov	r2, #1
	strb	ip, [sp, #3]
	bl	write(PLT)
	b	.L4
.L2:
	ldr	ip, .L7+8
	mov	r1, #1
	ldr	r0, .L7+20
	mov	r2, #21
	ldr	r3, [r3, ip]
.LPIC1:
	add	r0, pc, r0
	add	r3, r3, #84
	bl	fwrite(PLT)
	mvn	r0, #0
	add	sp, sp, #8
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, r7, r8, r9, r10, pc}
.L8:
	.align	2
.L7:
	.word	.LC0-(.LPIC0+8)
	.word	_GLOBAL_OFFSET_TABLE_-(.LPIC2+8)
	.word	__sF(GOT)
	.word	.LC2-(.LPIC3+8)
	.word	.LC3-(.LPIC4+8)
	.word	.LC1-(.LPIC1+8)
	.size	main, .-main
	.section	.rodata.str1.4,"aMS",%progbits,1
	.align	2
.LC0:
	.ascii	"/dev/kjh_fpgaled\000"
	.space	3
.LC1:
	.ascii	"can't open the driver\000"
	.space	2
.LC2:
	.ascii	"Input LED value [0-255] : \000"
	.space	1
.LC3:
	.ascii	"%d\000"
	.ident	"GCC: (GNU) 4.8"
	.section	.note.GNU-stack,"",%progbits
