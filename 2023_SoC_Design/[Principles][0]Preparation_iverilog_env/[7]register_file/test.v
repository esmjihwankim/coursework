`timescale 1ns/1ns
 
module test;
 
// delare variables
reg clock;
reg resetn;
reg [1:0] addr;
reg [3:0] din;
reg we;
 
wire [3:0] dout;
 
// clock generation
always #10 clock = ~clock;
 
regfile u_regfile (
    .CLK      (clock),
    .RSTn     (resetn),
    .ADDR     (addr),
    .WE       (we),
    .DIN      (din),
    .DOUT     (dout)
);
 
 
// create wave dump file
initial
begin
    $dumpfile("regfile.vcd");
    $dumpvars(0, test);
end
 
// input stimulus
initial
begin
    clock <= 0;
    resetn <= 0;
    we <= 0;
    #100;
    resetn <= 1;
    @(posedge clock);
    addr <= 2'd0;
    din <= 4'd1;
    we  <= 1;
    @(posedge clock);
    addr <= 2'd1;
    din <= 4'd2;
    @(posedge clock);
    addr <= 2'd2;
    din <= 4'd3;
    @(posedge clock);
    we <= 0;
    addr <= 0;
    @(posedge clock);
    addr <= 1;
    @(posedge clock);
    addr <= 2;
    #100;
    $finish();
end
 
endmodule