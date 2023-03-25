`timescale 1ns/1ns

module test_sub;

reg clock;
reg resetn;
reg [7:0] a;
reg [7:0] b; 
reg en; 

wire [7:0] y;

always #10 clock = ~clock;

subtractor u_sub (
    .clock(clock),
    .resetn(resetn),
    .en(en),
    .a(a),
    .b(b),
    .y(y)
); 

initial
begin
    $dumpfile("sub.vcd");
    $dumpvars(0, test_sub);
end

initial
begin
    a <= 0;
    b <= 0;
    en <= 0;
    clock <= 0; 
    resetn <= 0;
    #100; 
    resetn <= 1; 
    @(posedge clock);
    a <= 2; 
    b <= 3; 
    @(posedge clock);
    en <= 1;
    a <= 4;
    b <= 5; 
    @(posedge clock);
    a <= 10;
    b <= 30;
    @(posedge clock);
    a <= 33;
    b <= 11; 
    en <= 0;
    @(posedge clock);
    a <= 100;
    b <= 50;
    en <= 1;
    @(posedge clock);
    #100;
    $finish();
end
endmodule
