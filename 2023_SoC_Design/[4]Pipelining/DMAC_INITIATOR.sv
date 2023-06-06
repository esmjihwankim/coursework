//
// Copyright (c) 2023 Sungkyunkwan University
//
// Authors:
// - Jungrae Kim <dale40@skku.edu>
module DMAC_INITIATOR 
(
    input   wire                clk,
    input   wire                rst_n,

    /* FIXME: Declare your input/output port here */

    // Configuration registers
    input    wire    [31:0]    src_addr_i, 
    input    wire    [31:0]    dst_addr_i,
    input    wire    [15:0]    byte_len_i, 
    input    wire              start_i, 
    output   wire              done_o, 

    // AMBA AXI interface  (AR Channel)
    output   wire    [31:0]    araddr_o,    // start address 
    output   wire    [3:0]     arlen_o,     // number of transfers 
    output   wire    [2:0]     arsize_o,    // number of bytes per transfer 
    output   wire    [1:0]     arburst_o,   // burst type 
    output   wire              arvalid_o,
    input    wire              arready_i,

    // AMBA AXI interface  (R Channel)
    input    wire    [31:0]    rdata_i,     // requested chunks of data    
    input    wire    [1:0]     rresp_i,     // whether read succeeded
    input    wire              rlast_i,     // whether last piece of data in burst
    input    wire              rvalid_i,     
    output   wire              rready_o,    

    // AMBA AXI interface (AW Channel)
    output   wire    [31:0]    awaddr_o,    // start address
    output   wire    [3:0]     awlen_o,     // number of transfers 
    output   wire    [2:0]     awsize_o,    // number of bytes per transfer
    output   wire    [1:0]     awburst_o,   // burst type 
    output   wire              awvalid_o, 
    input    wire              awready_i,

    // AMBA AXI interface  (W Channel)
    output   wire    [31:0]    wdata_o,     // chunks of data to write 
    output   wire    [3:0]     wstrb_o,     // send in strobe 
    output   wire              wlast_o,     // whether last piece of data in burst 
    output   wire              wvalid_o,
    input    wire              wready_i,

    // AMBA AXI interface  (B Channel)
    input    wire    [1:0]     bresp_i,
    input    wire              bvalid_i,
    output   wire              bready_o
);

    /* FIXME: Write your code here (You may use FSM implementation here) */ 
    localparam          S_IDLE    = 2'd0,
                        S_BUSY    = 2'd1,
                        S_WAIT    = 2'd3; 
    
    reg     [2:0]       state,      state_n; 
    
    reg     [31:0]      src_addr,   src_addr_n; 
    reg     [31:0]      dst_addr,   dst_addr_n; 
    reg     [15:0]      cnt,        cnt_n; 
    reg     [3:0]       wcnt,       wcnt_n; 

    reg                 arvalid,
                        rready,
                        awvalid,
                        wvalid,
                        wlast,
                        done;

    /********************************************************/
    /************************ CFG  **************************/
    /********************************************************/
    /* Register updates for each clock */ 
    always_ff @(posedge clk)
        if(!rst_n) begin
            state        <=    S_IDLE; 
            
            src_addr     <=    32'd0;
            dst_addr     <=    32'd0; 
            cnt          <=    16'd0; 

            wcnt         <=    4'd0; 
        end else begin 
            state        <=    state_n; 

            src_addr     <=    src_addr_n; 
            dst_addr     <=    dst_addr_n;
            cnt          <=    cnt_n; 

            wcnt         <=    wcnt_n; 
        end

    /********************************************************/
    /************************ FSM  **************************/
    /********************************************************/
    /*  Finite State Machine for Initiator  */
    always_comb begin 
        state_n          =    state; 
        
        src_addr_n       =    src_addr; 
        dst_addr_n       =    dst_addr; 
        cnt_n            =    cnt; 
        wcnt_n           =    wcnt; 

        case (state)
            // Start operation when configuration register (CFG) set 
            S_IDLE: begin
                done          = 1'b1; 
                if(start_i & byte_len_i != 16'd0) begin 
                    src_addr_n           = src_addr_i; 
                    dst_addr_n           = dst_addr_i; 
                    cnt_n                = byte_len_i; 

                    state_n              = S_BUSY; 
                end
            end
            
            // Start the pipelining by sending an AR request                                                       
            S_BUSY: begin
                
            end
            
            // When Writing Done, a request will be received through B channel
            S_WAIT: begin
                // TODO: Implement 
            end
        endcase 
    end 

    /********************************************************/
    /**************** Pipelining ****************************/
    /********************************************************/
    // Variable for Initiator to AW FIFO 
    wire                init_to_aw_fifo_full;          // to sender 
    wire                init_to_aw_fifo_empty;         // to receiver
    reg                 init_to_aw_fifo_wren;          // from sender
    reg                 init_to_aw_fifo_rden;          // from receiver
    wire    [31:0]      init_to_aw_fifo_rdata;         // to receiver
    // Variable for R to W FIFO
    wire                r_to_w_fifo_full;              
    wire                r_to_w_fifo_empty;             
    wire                r_to_w_fifo_wren;              
    reg                 r_to_w_fifo_rden;             
    wire    [31:0]      r_to_w_fifo_rdata;            
    // sample
    wire                fifo_full;
    wire                fifo_empty;
    wire                fifo_rdata;

    // flag 
    reg                 arvalid_flag;
    
    /* FIFO for R to W Channel (Writing Data) */
    DMAC_FIFO #(
        .DEPTH_LG2               (4),
        .DATA_WIDTH              ($bits(wdata_o))
    ) u_r_to_w_fifo
    (
        .clk                    (clk),
        .rst_n                  (rst_n), 

        .full_o                 (r_to_w_fifo_full), 
        .wren_i                 (r_to_w_fifo_wren),
        .wdata_i                (rdata_i),

        .empty_o                (r_to_w_fifo_empty),
        .rden_i                 (r_to_w_fifo_rden),
        .rdata_o                (wdata_o)
    );

    assign              r_to_w_fifo_wren = rvalid_i & !r_to_w_fifo_full;       // manipulate write enable 
    assign              r_to_w_fifo_rden = wready_i & !r_to_w_fifo_empty;      // manipulate read enable 

    /* Manipulation of declared FIFOs for pipelining */
    always_ff @(posedge clk) begin
        // Send out AR Request 
        if(state == S_BUSY && !r_to_w_fifo_full) begin
            arvalid             <= 1'b1; 
            if(arvalid && arready_i) begin
                arvalid <= 1'b0;
            end
        end 
        else begin
            arvalid             <= 1'b0;
        end
        // When R received, save generated AW data in FIFO 
        

        // When R received, save R data in FIFO  
        if(state == S_BUSY && rvalid_i) begin
            rready              <= 1'b1; 

            if(rvalid_i && rready) begin
                rready          <= 1'b0;
            end
        end
        else begin
            rready              <= 1'b0; 
        end

    end


    /********************************************************/
    /**************** Output Assignments ********************/
    /********************************************************/
    // AR Channel
    assign arvalid_o    = arvalid;
    assign araddr_o     = src_addr;
    assign arlen_o      = (cnt >= 'd64) ? 4'hF : cnt[5:2]-4'h1; 
    assign arsize_o     = 3'b010;                                  // 4 bytes per transfer
    assign arburst_o    = 2'b01;                                   // incremental
    assign arvalid_o    = arvalid; 
    // R Channel
    assign rready_o     = rready & !r_to_w_fifo_full; 
    // AW Channel 
    assign awaddr_o     = dst_addr;
    assign awlen_o      = (cnt >= 'd64) ? 4'hF : cnt[5:2]-4'h1; 
    assign awsize_o     = 3'b010;                                  // 4 bytes per transfer
    assign awburst_o    = 2'b01;                                   // incremental
    assign awvalid_o    = awvalid;
    // W Channel
    assign wdata_o      = r_to_w_fifo_rdata; 
    assign wstrb_o      = 4'b1111;                                 // all bytes within 4 bytes are valid
    assign wlast_o      = wlast;                    
    assign wvalid_o     = wvalid;
    // B Channel 
    assign bready_o     = 1'b1; 
    // Others
    assign done_o       = done;

endmodule
// dmac_initiator written by Jihwan Kim
