`timescale 1ns/1ns

module test; 

reg clock;
reg resetn;
reg [7:0] a;
reg [7:0] b; 

wire [7:0] y; 

always #10 clock = ~clock; 

adder_seq u_adder_seq(
    .clock  (clock),
    .resetn (resetn),
    .a      (a),
    .b      (b),
    .y      (y) 
);

initial begin
    $dumpfile("adder_seq.vcd");
    $dumpvars(0,test);
end

initial 
begin
    a = 0;
    b = 0;
    clock = 0;
    resetn = 0; 
    #100; 
    resetn = 1;
    a = 2;
    b = 3;
    @(posedge clock);
    a = 4;
    b = 5; 
    @(posedge clock);
    a = 10;
    b = 30;
    @(posedge clock);
    #100;
    $finish();
end 
endmodule