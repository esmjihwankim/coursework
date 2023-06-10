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
                        S_WAIT    = 2'd2; 
    
    reg     [2:0]       state,      state_n; 
    
    reg     [31:0]      src_addr,                  src_addr_n; 
    reg     [31:0]      dst_addr,                  dst_addr_n; 
    reg     [15:0]      cnt,                       cnt_n; 
    reg     [3:0]       wcnt,                      wcnt_n; 

    reg                 arvalid,
                        rready,
                        awvalid,
                        wvalid,
                        wlast,              
                        done;

                        
    // Variable for R to W FIFO
    wire                r_to_w_fifo_full;              
    wire                r_to_w_fifo_empty;             
    wire                r_to_w_fifo_wren;              
    wire                r_to_w_fifo_rden;             
    wire    [31:0]      r_to_w_fifo_rdata;   
    reg     [5:0]       r_to_w_fifo_cnt;

    reg                 r_to_w_fifo_pop;

    // Channel Flags : activated during handshake 
    reg                 arflag;
    reg                 awflag;

    /********************************************************/
    /************************ CFG  **************************/
    /********************************************************/
    /* Register updates for each clock */ 
    always_ff @(posedge clk) begin
        if(!rst_n) begin
            state                     <=    S_IDLE; 
            
            src_addr                  <=    32'd0;
            dst_addr                  <=    32'd0; 
            cnt                       <=    16'd0; 

            wcnt                      <=    4'd0; 
        end 
        else begin 
            state                     <=    state_n; 

            src_addr                  <=    src_addr_n; 
            dst_addr                  <=    dst_addr_n;
            cnt                       <=    cnt_n; 

            wcnt                      <=    wcnt_n;
        end
    end

    /********************************************************/
    /************************ FSM  **************************/
    /********************************************************/
    /*  Finite State Machine for Initiator  */
    /*  Does most of acccounting operations */
    always_comb begin 
        state_n                 = state;

        src_addr_n              = src_addr;
        dst_addr_n              = dst_addr;
        cnt_n                   = cnt;
        wcnt_n                  = wcnt;

        case (state) 
            // Start operation when configuration register (CFG) set 
            S_IDLE: begin
                if (start_i & byte_len_i!=16'd0) begin
                    src_addr_n = src_addr_i;
                    dst_addr_n = dst_addr_i;
                    cnt_n = byte_len_i;

                    state_n = S_BUSY;
                end
            end

            // Start the pipelining 
            S_BUSY: begin
                // AR Channel
                if(arvalid && arready_i) begin
                    src_addr_n = src_addr + 'd64; 
                end 
                // AW CHANNEL handshake incurs address accounting operations  
                if(awvalid && awready_i) begin 
                    dst_addr_n = dst_addr + 'd64; 
                    wcnt_n = awlen_o;
                    if(cnt_n > 'd64) begin
                        cnt_n = cnt_n - 'd64;
                    end 
                    else begin 
                        cnt_n = 0; 
                    end 
                end 

                // W channel handshake incurs decrementing write count 
                if(wready_i && wvalid) begin
                    if(wlast) begin
                        if(cnt == 16'd0) begin
                            state_n = S_WAIT;
                        end     
                    end
                    else begin
                        wcnt_n = wcnt - 4'd1; 
                    end
                end

                if(wlast && (cnt == 0)) begin
                    state_n = S_IDLE;
                end
            end
        endcase
    end 

    /********************************************************/
    /**************** Pipelining ****************************/
    /********************************************************/
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
        .rdata_o                (r_to_w_fifo_rdata)
    );
    
    /* Control Wiring for FIFO                                                                             */
    /* change in AW, R, W channel valid/ready automatically adjusts the FIFO read enable and write enables */
    assign  r_to_w_fifo_wren         = (rvalid_i & rready_o) & !r_to_w_fifo_full;      
    assign  r_to_w_fifo_rden         = (((wvalid & wready_i) & (!r_to_w_fifo_empty)));   

    /* Manipulation of declared FIFOs for pipelining  */
    /* does most of signal driving operations         */
    always_ff @(posedge clk) begin
        // reset signal
        if(!rst_n) begin
            arvalid                   <= 1'b0;
            rready                    <= 1'b0;
            awvalid                   <= 1'b0;
            wvalid                    <= 1'b0;
            wlast                     <= 1'b0;
            done                      <= 1'b0;

            arflag                    <= 1'b0;
            awflag                    <= 1'b0;
            
            r_to_w_fifo_cnt           <= 5'b0;
            r_to_w_fifo_pop           <= 1'b0;
        end
        // reset signal off 
        else begin                   
            // IDLE state
            if(state == S_IDLE)begin
                done <= 1'b1;
                if(start_i) begin
                    done <= 1'b0;
                    arflag <= 1'b1;
                end
            end
        
            // AR 
            // arflag    : ______----------_________
            // arvalid_o : _________-------_________
            // arready_i : ______________--_________
            if (state == S_BUSY && arflag) begin  // BUSY state and Done means its 
                arvalid = 1'b1;
                if(arvalid && arready_i) begin
                    arvalid <= 1'b0;
                    arflag <= 1'b0;
                end
            end 
            else begin // dummy to prevent latch
            end

            // Receive R 
            // When R received, save R data in FIFO
            // Contains AW Generation Control
            if( (state == S_BUSY) && rvalid_i) begin
                rready  <= 1'b1; 
                // handshake
                if(rvalid_i && rready && !r_to_w_fifo_full)begin  // read channel valid-ready handshake occurs depending on the FIFO condition  
                    rready <= 1'b0; 
                    r_to_w_fifo_cnt <= r_to_w_fifo_cnt + 'd1;
                    // Start AW Generation 
                    // AW GENERATION
                    // !awflag     : -----------------_______
                    // awvalid_o   : ________---------_______
                    // awready_i   : ______________---_______
                    awvalid <= 1'b1;
                    if(awvalid && awready_i) begin
                        awvalid <= 1'b0;
                    end
                end
            end
            else begin
                rready <= 1'b0; 
            end

            // Write on W channel 
            // When u_r_to_w_fifo has values, read out the value of the write 
            // wdata_o    : --data--________-data-_______
            // wvalid_o   : -------------------------------
            // wready_i   : ______--____________--_______
            if( (state == S_BUSY) && (r_to_w_fifo_cnt > 5'd1)) begin
                wvalid <= 1'b1; 
                // handshake
                if(wvalid && wready_i) begin
                    r_to_w_fifo_cnt <= r_to_w_fifo_cnt - 'd1;
                end
            end
            else begin
                wvalid <= 1'b0;  // data not ready to be given
            end
   
            // last flag 
            if((state == S_BUSY) && (wcnt == 4'd0)) begin
                wlast <= 1'b1;
            end 
            else begin
                wlast <= 1'b0;
            end 

            // Loop back to RREQ phase or Wait
            // At this point, a set of writings have been done
            if((state == S_BUSY) && wlast) begin
                if(cnt != 0) begin
                    arvalid <= 1'b1;
                end
                else begin
                    arvalid <= 1'b0;
                end
            end
            else begin // dummy to prevent latch formation
            end
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

