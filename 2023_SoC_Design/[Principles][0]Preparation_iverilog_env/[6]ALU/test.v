`timescale 1ns/1ns

module test; 

reg clock;
reg resetn;
reg [7:0] a;
reg [7:0] b; 
reg [2:0] shift_num;
reg [1:0] opcode;

wire [7:0] y; 
wire [1:0] opOut; 

always #10 clock = ~clock;

alu u_alu(
    .clock(clock),
    .resetn(resetn),
    .opA(a),
    .opB(b), 
    .opcode(opcode), 
    .shift_num(shift_num),
    .y(y),
    .opOut(opOut)
); 

initial 
begin
    $dumpfile("alu.vcd");
    $dumpvars(0,test);    
end

parameter OP_ADD = 2'b00;
parameter OP_SUB = 2'b01;
parameter OP_SHIFT_R = 2'b10;
parameter OP_SHIFT_L = 2'b11; 


initial 
begin   
    clock <= 0;
    resetn <= 0;
    #100;
    resetn <= 1; 
    @(posedge clock);
    opcode <= OP_ADD;
    a <= 1;
    b <= 2;
    @(posedge clock);
    opcode <= OP_SUB;
    a <= 3;
    b <= 1;
    @(posedge clock);
    a <= 3;
    opcode = OP_SHIFT_L;
    shift_num <= 2;
    @(posedge clock); 
    a <= 4;
    opcode <= OP_SHIFT_R; 
    shift_num <= 1;
    @(posedge clock);
    #100;
    $finish(); 
end
endmodule