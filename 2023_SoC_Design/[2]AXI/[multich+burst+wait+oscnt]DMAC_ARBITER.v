// Copyright (c) 2021 Sungkyunkwan University
//
// Authors:
// - Jungrae Kim <dale40@skku.edu>
// - Jihwan Kim 

module DMAC_ARBITER
#(
    N_MASTER                    = 4,
    DATA_SIZE                   = 32
)
(
    input   wire                clk,
    input   wire                rst_n,  // _n means active low

    // configuration registers
    input   wire                src_valid_i[N_MASTER],
    output  reg                 src_ready_o[N_MASTER],
    input   wire    [DATA_SIZE-1:0]     src_data_i[N_MASTER],

    output  reg                 dst_valid_o,
    input   wire                dst_ready_i,
    output  reg     [DATA_SIZE-1:0] dst_data_o
);
    // TODO: implement your arbiter here

    // ------------------- internal registers ---------------------- 
    reg [31:0]datapool_1 [5],
        [31:0]datapool_2 [5],
        [31:0]datapool_3 [5],
        [31:0]datapool_4 [5]; 

    // --------------------------Input FSM---------------------------------
    // AR, W, AW requests always have data flowing from Master to Slave 
    // general workflow 

    // clk                          : __--__--__--__--__--__--__--__--
    // rst_n                        : -----___________________________
    // src_valid_i                  : _______--------------___________
    // src_ready_o                  : __________-----------___________
    // [31:0] src_data_i [N_MASTER] :            |SRCDATA| 
    // 
    // dst_valid_o                  : _______________________--------
    // dst_ready_i                  : ____________________________---
    // [31:0] dst_data_o [N_MASTER] :                             |DSTDATA|
    // ------------------------------------------------------------

    localparam    S_IDLE  = 3'd0, 
                  S_CHECK = 3'd1,
                  S_STORE = 3'd2,
                  S_POP   = 3'd3;

    always_ff @(posedge clk or negedge rst_n) begin 
        if(~rst_n) begin
            

        end 
    end 
    



    // ---------------------OUTPUT FSM -------------------
    always_ff(@posedge clk or negedge rst_n) begin 
        if(~rst_n) begin


        end 
    end 




endmodule
