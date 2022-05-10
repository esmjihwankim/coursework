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
	.file	"kjh_fpgaADC_test.c"
	.section	.text.startup,"ax",%progbits
	.align	2
	.global	main
	.type	main, %function
main:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	ldr	r0, .L5
	movw	r1, #4098
	stmfd	sp!, {r3, r4, r5, lr}
.LPIC0:
	add	r0, pc, r0
	bl	open(PLT)
	ldr	r4, .L5+4
.LPIC2:
	add	r4, pc, r4
	subs	r5, r0, #0
	blt	.L4
	mov	r2, #0
	movw	r1, #21809
	mov	r3, r2
	bl	ioctl(PLT)
	ldr	r3, .L5+8
	ldr	r0, .L5+12
	mov	r1, #1
	mov	r2, #13
	ldr	r3, [r4, r3]
.LPIC3:
	add	r0, pc, r0
	add	r3, r3, #84
	bl	fwrite(PLT)
	mov	r0, r5
	bl	close(PLT)
	mov	r0, #0
	ldmfd	sp!, {r3, r4, r5, pc}
.L4:
	ldr	r3, .L5+8
	mov	r1, #1
	ldr	r0, .L5+16
	mov	r2, #21
	ldr	r3, [r4, r3]
.LPIC1:
	add	r0, pc, r0
	add	r3, r3, #84
	bl	fwrite(PLT)
	mov	r0, #1
	bl	exit(PLT)
.L6:
	.align	2
.L5:
	.word	.LC0-(.LPIC0+8)
	.word	_GLOBAL_OFFSET_TABLE_-(.LPIC2+8)
	.word	__sF(GOT)
	.word	.LC2-(.LPIC3+8)
	.word	.LC1-(.LPIC1+8)
	.size	main, .-main
	.section	.rodata.str1.4,"aMS",%progbits,1
	.align	2
.LC0:
	.ascii	"/dev/kjh_fpgaADC\000"
	.space	3
.LC1:
	.ascii	"can't open the driver\000"
	.space	2
.LC2:
	.ascii	"ADC Active ::\000"
	.ident	"GCC: (GNU) 4.8"
	.section	.note.GNU-stack,"",%progbits
