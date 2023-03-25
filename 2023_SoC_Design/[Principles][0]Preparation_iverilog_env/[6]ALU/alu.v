module alu ( 
    input clock,
    input resetn, 
    input [7:0] opA,
    input [7:0] opB, 
    input [1:0] opcode,
    input [2:0] shift_num, 
    output [7:0] y, 
    output reg [1:0] opOut
);

wire left_right;
wire [7:0] sum;
wire [7:0] sub;
wire [7:0] shift; 

assign left_right = opcode[0];

adder u_adder(
    .clock(clock),
    .resetn(resetn),
    .a(opA), 
    .b(opB),
    .y(sum)
); 

subtractor u_sub(
    .clock(clock),
    .resetn(resetn),
    .a(opA),
    .b(opB),
    .en(1'b1),
    .y(sub)
); 

barrel_shifter u_shift(
    .clock(clock),
    .resetn(resetn),
    .a(opA),
    .num(shift_num),
    .left_right(left_right),
    .y(shift)
); 

mux u_mux (
    .in0(sum),
    .in1(sub),
    .in2(shift),
    .in3(shift),
    .sel(opOut),
    .out(y)
); 

always @(posedge clock or negedge resetn)
begin
    if(!resetn)
        opOut <= 0;
    else 
        opOut <= opcode;
end 
endmodule

module mux(
    input [7:0] in0,
    input [7:0] in1, 
    input [7:0] in2,
    input [7:0] in3,
    input [1:0] sel,
    output reg [7:0] out
); 

always @(*)
begin 
    case(sel)
    2'b00:
        out = in0;
    2'b01:
        out = in1;
    2'b10:
        out = in2;
    2'b11:
        out = in3;
    default:
        out = 8'b0;
    endcase
end
endmodule
