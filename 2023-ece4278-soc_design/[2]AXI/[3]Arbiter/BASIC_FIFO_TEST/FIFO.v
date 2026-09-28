module FIFO #(
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH = 8
)(
    input wire                 clk,
    input wire                 rst_n,
    input wire                 wren_i, 
    input wire                 rden_i, 
    input  [DATA_WIDTH-1:0]    wdata_i,
    
    output [DATA_WIDTH-1:0]    rdata_o, 
    output                     full_o,
    output                     empty_o
);

    // bit number 
    localparam FIFO_DEPTH_LG2 = $clog2(FIFO_DEPTH); 

    reg[FIFO_DEPTH_LG2:0] rdptr;
    reg[FIFO_DEPTH_LG2:0] wrptr; 
    
    // write point counter seuqential logic 
    always @(posedge clk, negedge rst_n) begin
        if(!rst_n) begin
            wrptr <= {(FIFO_DEPTH_LG2+1){1'b0}};
        end else if (wren_i) begin
            wrptr <= wrptr + 'd1; 
        end
    end

    // read pointer counter seq logic 
    always @(posedge clk, negedge rst_n) begin
        if(!rst_n) begin
            rdptr <= {(FIFO_DEPTH_LG2+1){1'b0}};
        end else if (rden_i) begin
            rdptr <= rdptr + 'd1;
        end
    end

    reg[DATA_WIDTH-1:0] mem[0:FIFO_DEPTH-1];  // 31 bits of data, 8 locations 

    // Write 
    always @(posedge clk) begin
        if(wren_i) begin
            mem[wrptr[FIFO_DEPTH_LG2-1:0]] <= wdata_i;
        end
    end 

    // Read 
    assign rdata_o = mem[rdptr[FIFO_DEPTH_LG2-1:0]];

    assign empty_o = (wrptr==rdptr); 
    assign full_o = (wrptr[FIFO_DEPTH_LG2-1:0] == rdptr[FIFO_DEPTH_LG2-1:0]) & 
                        (wrptr[FIFO_DEPTH_LG2] != rdptr[FIFO_DEPTH_LG2]); 
    
endmodule
    

/*
    input   wire                src_valid_i[4],
    output  reg                 src_ready_o[4],
    input   wire    [31:0]     src_data_i[4],

    output  reg                 dst_valid_o,
    input   wire                dst_ready_i,
    output  reg     [31:0]      dst_data_o
*/
    
