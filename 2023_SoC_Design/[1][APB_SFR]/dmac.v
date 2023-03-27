// Copyright (c) 2021 Sungkyunkwan University
//
// Authors:
// - Jungrae Kim <dale40@skku.edu>
// - Jihwan Kim <jihwan.kim@g.skku.edu>

module DMAC_CFG
(
    input   wire                clk,
    input   wire                rst_n,  // _n means active low

    // AMBA APB interface
    input   wire                psel_i,
    input   wire                penable_i,
    input   wire    [11:0]      paddr_i,
    input   wire                pwrite_i,
    input   wire    [31:0]      pwdata_i,
    output  reg                 pready_o,
    output  reg     [31:0]      prdata_o,
    output  reg                 pslverr_o,

    // configuration registers
    output  reg     [31:0]      src_addr_o,
    output  reg     [31:0]      dst_addr_o,
    output  reg     [15:0]      byte_len_o,
    output  wire                start_o,
    input   wire                done_i
);

    // Configuration register to read/write
    reg     [31:0]              src_addr;
    reg     [31:0]              dst_addr;
    reg     [15:0]              byte_len;

    //----------------------------------------------------------
    // Write
    //----------------------------------------------------------
    // an APB write occurs when PSEL & PENABLE & PWRITE
    // clk     : __--__--__--__--__--__--__--__--__--__--
    // psel    : ___--------_____________________________
    // penable : _______----_____________________________
    // pwrite  : ___--------_____________________________
    // wren    : _______----_____________________________
    //
    // DMA start command must be asserted when APB writes 1 to the DMA_CMD
    // register
    // clk     : __--__--__--__--__--__--__--__--__--__--     //
    // psel    : ___--------_____________________________     //
    // penable : _______----_____________________________     // 
    // pwrite  : ___--------_____________________________     //
    // paddr   :    |DMA_CMD|                                 //
    // pwdata  :    |   1   |                                 //
    // start   : _______----_____________________________

    wire    wren;
    assign  wren                = // fill your code here
    always @(posedge clk) begin
        // fill
        // your
        // code
        // here
    end
    wire    start;
    assign  start               = // fill your code here

    // Read
    reg     [31:0]              rdata;

    //----------------------------------------------------------
    // READ
    //----------------------------------------------------------
    // an APB read occurs when PSEL & PENABLE & !PWRITE
    // To make read data a direct output from register,
    // this code shall buffer the muxed read data into a register
    // in the SETUP cycle (PSEL & !PENABLE)
    // clk        : __--__--__--__--__--__--__--__--__--__--
    // psel       : ___--------_____________________________
    // penable    : _______----_____________________________
    // pwrite     : ________________________________________
    // reg update : ___----_________________________________
    //
    always @(posedge clk) begin
        // fill
        // your
        // code
        // here
    end

    // output assignments
    assign  pready_o            = 1'b1;
    assign  prdata_o            = rdata;
    assign  pslverr_o           = 1'b0;

    assign  src_addr_o          = src_addr;
    assign  dst_addr_o          = dst_addr;
    assign  byte_len_o          = byte_len;
    assign  start_o             = start;

endmodule