`timescale 1ns/1ns
 
module test;
 
// delare variables
reg clock;
reg resetn;
reg [7:0] a;
reg [2:0] num;
reg left_right;
 
wire [7:0] y;
 
// clock generation
always #10 clock = ~clock;
 
// shifter instantiation
barrel_shifter u_shifter (
    .clock  (clock),
    .resetn (resetn),
	.a      (a),
    .num    (num),
    .left_right (left_right),
    .y      (y)
);
 
 
// create wave dump file
initial
begin
    $dumpfile("shifter.vcd");
    $dumpvars(0, test);
end
 
// input stimulus
initial
begin
    a <= 0;
    num <= 0;
    left_right <= 0;
    clock <= 0;
    resetn <= 0;
    #100;
    resetn <= 1;
    a <= 2;
    num <= 1;
    @(posedge clock);
    left_right <= 1;
    a <= 4;
    num <= 2;
    @(posedge clock);
    #100;
    $finish();
end
 
endmodule