

module data_fifo (
    input wire clk,
    input wire rst_n,

    input wire [31:0] datastream [4]
);

    localparam FIFO_DEPTH = 'd8,
               DATA_WIDTH = 'd32; 
               DATA_DEPTH = 'd4; 

    reg[DATA_WIDTH-1:0] datastore[FIFO_DEPTH]; 
    
    reg full, full_n, 
        empty, empty_n;
    reg [DATA_DEPTH-1:0]  wrptr, wrptr_n, 
                       rdptr, rdptr_n;

    always_ff @(posedge clk) begin
        if(!rst_n) begin

        end
        else begin
            full <= full_n; 

        end 
    end

    

    
    
