
`timescale 1ns/1ns

module test; 
// input can be reg, output has to be wire 

reg clk; 
reg resetn;
reg d;
wire q; 

// clock generation 
always #10 clk = ~clk;

// DUT
dff u_dff (
    .clk(clk),
    .resetn(resetn),
    .d(d),
    .q(q)
);

initial
begin
    $dumpfile("dff.vcd");
    $dumpvars(0, test);
end

initial
begin
    clk     <= 0;       // non blocking assignment 
    resetn  <= 0;       
    d       <= 0;
    @(posedge clk);     // wait for the next positive edge
    @(posedge clk);
    @(posedge clk);
    @(posedge clk);
    d       <= 1;
    @(posedge clk);
    resetn  <= 1;
    @(posedge clk);
    @(posedge clk);
    @(posedge clk);
    d       <= 0;
    @(posedge clk);
    @(posedge clk);
    d       <= 1;
    @(posedge clk);
    @(posedge clk);
    $finish(); 
end 

endmodule



