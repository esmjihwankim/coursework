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
	.file	"kjh_fpgaFullColorLED_test.c"
	.text
	.align	2
	.global	input_value
	.type	input_value, %function
input_value:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 0, uses_anonymous_args = 0
	ldr	r0, .L2
	mov	r3, #0
	stmfd	sp!, {r4, r5, r6, lr}
	sub	sp, sp, #8
	ldr	r4, .L2+4
.LPIC0:
	add	r0, pc, r0
	strh	r3, [sp, #4]	@ movhi
	add	r6, sp, #4
	strb	r3, [sp, #6]
	bl	puts(PLT)
	ldr	r0, .L2+8
.LPIC2:
	add	r4, pc, r4
	ldr	r5, .L2+12
.LPIC1:
	add	r0, pc, r0
	bl	printf(PLT)
	mov	r1, r6
	mov	r0, r4
.LPIC7:
	add	r5, pc, r5
	bl	scanf(PLT)
	ldr	r0, .L2+16
.LPIC3:
	add	r0, pc, r0
	bl	printf(PLT)
	add	r1, sp, #5
	mov	r0, r4
	bl	scanf(PLT)
	ldr	r0, .L2+20
.LPIC5:
	add	r0, pc, r0
	bl	printf(PLT)
	add	r1, sp, #6
	mov	r0, r4
	bl	scanf(PLT)
	mov	r0, #10
	bl	putchar(PLT)
	ldr	r3, .L2+24
	mov	r1, r6
	mov	r2, #3
	ldr	r3, [r5, r3]
	ldr	r0, [r3]
	bl	write(PLT)
	add	sp, sp, #8
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, pc}
.L3:
	.align	2
.L2:
	.word	.LC0-(.LPIC0+8)
	.word	.LC2-(.LPIC2+8)
	.word	.LC1-(.LPIC1+8)
	.word	_GLOBAL_OFFSET_TABLE_-(.LPIC7+8)
	.word	.LC3-(.LPIC3+8)
	.word	.LC4-(.LPIC5+8)
	.word	fd(GOT)
	.size	input_value, .-input_value
	.align	2
	.global	print_menu
	.type	print_menu, %function
print_menu:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r3, r4, r5, lr}
	mov	r0, #10
	ldr	r4, .L5
	bl	putchar(PLT)
	ldr	r5, .L5+4
.LPIC8:
	add	r4, pc, r4
.LPIC10:
	add	r5, pc, r5
	mov	r0, r4
	bl	puts(PLT)
	ldr	r0, .L5+8
.LPIC9:
	add	r0, pc, r0
	bl	puts(PLT)
	mov	r0, r5
	bl	puts(PLT)
	ldr	r0, .L5+12
.LPIC11:
	add	r0, pc, r0
	bl	puts(PLT)
	ldr	r0, .L5+16
.LPIC12:
	add	r0, pc, r0
	bl	puts(PLT)
	ldr	r0, .L5+20
.LPIC13:
	add	r0, pc, r0
	bl	puts(PLT)
	ldr	r0, .L5+24
.LPIC14:
	add	r0, pc, r0
	bl	puts(PLT)
	ldr	r0, .L5+28
.LPIC15:
	add	r0, pc, r0
	bl	puts(PLT)
	mov	r0, r5
	bl	puts(PLT)
	mov	r0, r4
	ldmfd	sp!, {r3, r4, r5, lr}
	b	puts(PLT)
.L6:
	.align	2
.L5:
	.word	.LC5-(.LPIC8+8)
	.word	.LC7-(.LPIC10+8)
	.word	.LC6-(.LPIC9+8)
	.word	.LC8-(.LPIC11+8)
	.word	.LC9-(.LPIC12+8)
	.word	.LC10-(.LPIC13+8)
	.word	.LC11-(.LPIC14+8)
	.word	.LC12-(.LPIC15+8)
	.size	print_menu, .-print_menu
	.align	2
	.global	ItemSelect
	.type	ItemSelect, %function
ItemSelect:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r3, r4, r5, r6, r7, lr}
	ldr	r6, .L22
	ldr	r3, .L22+4
.LPIC19:
	add	r6, pc, r6
	ldr	r5, .L22+8
	ldr	r7, .L22+12
	ldr	r4, [r6, r3]
.LPIC18:
	add	r5, pc, r5
.LPIC20:
	add	r7, pc, r7
.L8:
	bl	print_menu(PLT)
	mov	r0, r5
	bl	printf(PLT)
	ldr	r3, [r4, #4]
	sub	r3, r3, #1
	str	r3, [r4, #4]
	cmp	r3, #0
	blt	.L21
	ldr	r3, [r4]
	add	r2, r3, #1
	str	r2, [r4]
	ldrb	r0, [r3]	@ zero_extendqisi2
.L10:
	sub	r3, r0, #49
	cmp	r3, #4
	addls	pc, pc, r3, asl #2
	b	.L11
.L13:
	b	.L12
	b	.L14
	b	.L15
	b	.L16
	b	.L19
.L19:
	mov	r0, #0
	ldmfd	sp!, {r3, r4, r5, r6, r7, pc}
.L16:
	ldr	r3, .L22+16
	mov	r1, #6
	ldr	r3, [r6, r3]
	ldr	r0, [r3]
	bl	ioctl(PLT)
	bl	input_value(PLT)
	b	.L8
.L15:
	ldr	r3, .L22+16
	mov	r1, #7
	ldr	r3, [r6, r3]
	ldr	r0, [r3]
	bl	ioctl(PLT)
	bl	input_value(PLT)
	b	.L8
.L14:
	ldr	r3, .L22+16
	mov	r1, #8
	ldr	r3, [r6, r3]
	ldr	r0, [r3]
	bl	ioctl(PLT)
	bl	input_value(PLT)
	b	.L8
.L12:
	ldr	r3, .L22+16
	mov	r1, #9
	ldr	r3, [r6, r3]
	ldr	r0, [r3]
	bl	ioctl(PLT)
	bl	input_value(PLT)
	b	.L8
.L11:
	mov	r0, r7
	bl	printf(PLT)
	b	.L8
.L21:
	mov	r0, r4
	bl	__srget(PLT)
	uxtb	r0, r0
	b	.L10
.L23:
	.align	2
.L22:
	.word	_GLOBAL_OFFSET_TABLE_-(.LPIC19+8)
	.word	__sF(GOT)
	.word	.LC13-(.LPIC18+8)
	.word	.LC14-(.LPIC20+8)
	.word	fd(GOT)
	.size	ItemSelect, .-ItemSelect
	.section	.text.startup,"ax",%progbits
	.align	2
	.global	main
	.type	main, %function
main:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	ldr	r0, .L27
	movw	r1, #4098
	stmfd	sp!, {r4, lr}
.LPIC21:
	add	r0, pc, r0
	bl	open(PLT)
	ldr	r3, .L27+4
	ldr	r2, .L27+8
.LPIC22:
	add	r3, pc, r3
	ldr	r4, [r3, r2]
	cmp	r0, #0
	str	r0, [r4]
	blt	.L26
	bl	ItemSelect(PLT)
	ldr	r0, [r4]
	bl	close(PLT)
	mov	r0, #0
	ldmfd	sp!, {r4, pc}
.L26:
	ldr	r0, .L27+12
.LPIC23:
	add	r0, pc, r0
	bl	perror(PLT)
	mov	r0, #1
	bl	exit(PLT)
.L28:
	.align	2
.L27:
	.word	.LC15-(.LPIC21+8)
	.word	_GLOBAL_OFFSET_TABLE_-(.LPIC22+8)
	.word	fd(GOT)
	.word	.LC16-(.LPIC23+8)
	.size	main, .-main
	.comm	fd,4,4
	.section	.rodata.str1.4,"aMS",%progbits,1
	.align	2
.LC0:
	.ascii	"\012input range 0 ~ 100 \000"
	.space	2
.LC1:
	.ascii	"\012input Red value : \000"
.LC2:
	.ascii	"%d\000"
	.space	1
.LC3:
	.ascii	"\012input Green value : \000"
	.space	2
.LC4:
	.ascii	"\012input Blue value : \000"
	.space	3
.LC5:
	.ascii	"==============================================\000"
	.space	1
.LC6:
	.ascii	"                Select Menu\000"
.LC7:
	.ascii	"----------------------------------------------\000"
	.space	1
.LC8:
	.ascii	"   1.   Led1    -[1]\000"
	.space	3
.LC9:
	.ascii	"   2.   Led2    -[2]\000"
	.space	3
.LC10:
	.ascii	"   3.   Led3    -[3]\000"
	.space	3
.LC11:
	.ascii	"   4.   Led4    -[4]\000"
	.space	3
.LC12:
	.ascii	"   5.   Quit    -[5]\000"
	.space	3
.LC13:
	.ascii	"\012Selected Item :  \000"
	.space	1
.LC14:
	.ascii	"\012No Test Menu Selected\000"
	.space	1
.LC15:
	.ascii	"/dev/fpga_fullcolorled\000"
	.space	1
.LC16:
	.ascii	"/dev/fullcolorled open fail\012\000"
	.ident	"GCC: (GNU) 4.8"
	.section	.note.GNU-stack,"",%progbits
