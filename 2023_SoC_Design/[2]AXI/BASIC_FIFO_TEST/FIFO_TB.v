`timescale 1ps/1ps
`define CLOCK_PERIOD 10
`define DELTA 1 



module FIFO_TB #(
    parameter DATA_WIDTH = 8, 
    parameter FIFO_DEPTH = 8
)
(
); 

reg clk; 
reg rst_n; 
reg wren_i;
reg rden_i;
reg  [DATA_WIDTH-1:0]    wdata_i;
wire [DATA_WIDTH-1:0]    rdata_o;

wire full_o;
wire empty_o;

// DUT 
FIFO #(
    .DATA_WIDTH(DATA_WIDTH),
    .FIFO_DEPTH(FIFO_DEPTH)
) u_FIFO(
    .clk     (clk),
    .rst_n   (rst_n),
    .wren_i  (wren_i),
    .rden_i  (rden_i),
    .wdata_i (wdata_i),
    .rdata_o (rdata_o),
    .full_o  (full_o),
    .empty_o (empty_o)
); 


    initial begin
        clk = 1'b0; 
        forever begin 
            #(`CLOCK_PERIOD/2) clk = ~clk;
        end
    end

    integer i; 

    // Stimulus 
    // Init -> reset -> write -> read 
    initial begin 
        // step 0 initialize 
        rst_n = 1'b1;
        wren_i = 1'b0;
        rden_i = 1'b0;
        wdata_i = {(DATA_WIDTH){1'b0}};

        // step 1 reset 
        @(posedge clk);
        #(`DELTA)
        rst_n = 1'b0;

        @(posedge clk);
        #(`DELTA)
        rst_n = 1'b1;

        // step 2 write activation 
        for(i=0; i< FIFO_DEPTH; i=i+1) begin
            @(posedge(clk));
            #(`DELTA)
            wren_i  = 1'b1;
            wdata_i = i;
        end

        // step 3 write off 
        @(posedge clk);
        #(`DELTA)
        wren_i = 1'b0;

        // step 4 read activation
        for (i=0; i < FIFO_DEPTH; i=i+1) begin
            @(posedge clk);
            #(`DELTA)
            rden_i = 1'b1;
        end

        // step 5 read off 
        @(posedge clk);
        #(`DELTA)
        rden_i = 1'b0;
    end

    initial begin 
        $dumpfile("dump.vcd");
        $dumpvars(1, FIFO_TB);
        $display(":::FIFO TEST:::");
        #300 $finish; 
    end


endmodule
