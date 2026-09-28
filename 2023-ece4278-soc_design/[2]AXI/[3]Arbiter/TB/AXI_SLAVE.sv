`include "../TB/AXI_TYPEDEF.svh"

module AXI_SLAVE
#(
    parameter ADDR_WIDTH        = 16,
    parameter DATA_WIDTH        = `AXI_DATA_WIDTH,
    parameter ID_WIDTH          = `AXI_ID_WIDTH,
    parameter AWREADY_DELAY     = 1,
    parameter ARREADY_DELAY     = 1,
    parameter AR2R_DELAY        = 50
)
(
    input   wire                clk,
    input   wire                rst_n,  // _n means active low

    AXI_AW_CH                   aw_ch,
    AXI_W_CH                    w_ch,
    AXI_B_CH                    b_ch,
    AXI_AR_CH                   ar_ch,
    AXI_R_CH                    r_ch
);

    localparam  DATA_DEPTH      = 1<<ADDR_WIDTH;

    logic   [7:0]               mem[DATA_DEPTH];

    function void write_byte(int addr, input bit [7:0] wdata);
        mem[addr]               = wdata;
    endfunction

    function void write_word(int addr, input bit [31:0] wdata);
        for (int i=0; i<4; i++) begin
            write_byte(addr+i, wdata[8*i +: 8]);    // [i*8+7:i*8]
        end
    endfunction

    function bit [7:0] read_byte(int addr);
        read_byte               = mem[addr];
    endfunction

    function bit [31:0] read_word(int addr);
        for (int i=0; i<4; i++) begin
            read_word[8*i +: 8] = read_byte(addr+i);// [i*8+7:i*8]
        end
    endfunction

    //----------------------------------------------------------
    // write channels (AW, W, B)
    //----------------------------------------------------------
    localparam logic [1:0]      S_W_IDLE = 0,
                                S_W_AWREADY = 1,
                                S_W_BURST = 2,
                                S_W_RESP = 3;

    logic   [1:0]               wstate,             wstate_n;
    logic   [7:0]               wcnt,               wcnt_n;

    logic   [ADDR_WIDTH-1:0]    waddr,              waddr_n;
    logic   [ID_WIDTH-1:0]      wid,                wid_n;
    logic   [3:0]               wlen,               wlen_n;

    always_ff @(posedge clk)
        if (!rst_n) begin
            wstate              <= S_W_IDLE;

            wcnt                <= 8'd0;
            waddr               <= {ADDR_WIDTH{1'b0}};
            wid                 <= {ID_WIDTH{1'b0}};
            wlen                <= 4'd0;
        end
        else begin
            wstate              <= wstate_n;

            wcnt                <= wcnt_n;
            waddr               <= waddr_n;
            wid                 <= wid_n;
            wlen                <= wlen_n;
        end

    always @(*) begin
        wstate_n                = wstate;

        wcnt_n                  = wcnt;
        waddr_n                 = waddr;
        wid_n                   = wid;
        wlen_n                  = wlen;

        aw_ch.awready           = 1'b0;
        w_ch.wready             = 1'b0;
        b_ch.bvalid             = 1'b0;

        case (wstate)
            S_W_IDLE: begin
                if (aw_ch.awvalid) begin
                    if (AWREADY_DELAY == 0) begin
                        waddr_n                 = aw_ch.awaddr;
                        wid_n                   = aw_ch.awid;
                        wlen_n                  = aw_ch.awlen;
                        aw_ch.awready           = 1'b1;
                        wstate_n                = S_W_BURST;
                    end
                    else begin
                        wcnt_n                  = AWREADY_DELAY-1;
                        wstate_n                = S_W_AWREADY;
                    end
                end
            end
            S_W_AWREADY: begin
                if (wcnt==0) begin
                    waddr_n                 = aw_ch.awaddr;
                    wid_n                   = aw_ch.awid;
                    wlen_n                  = aw_ch.awlen;
                    aw_ch.awready           = 1'b1;
                    wstate_n                = S_W_BURST;
                end
                else begin
                    wcnt_n                  = wcnt - 8'd1;
                end
            end
            S_W_BURST: begin
                w_ch.wready             = 1'b1;
                if (w_ch.wvalid) begin
                    for (int i=0; i<DATA_WIDTH/8; i++) begin
                        write_byte(waddr + i, w_ch.wdata[i*8 +: 8]);    // [i*8+7:i*8]
                    end
                    waddr_n             = waddr + (DATA_WIDTH/8);
                    if (wlen==4'd0) begin
                        wstate_n                = S_W_RESP;
                    end
                    else begin
                        wlen_n              = wlen - 4'd1;
                    end
                end
            end
            S_W_RESP: begin
                b_ch.bvalid             = 1'b1;
                if (b_ch.bready) begin
                    wstate_n                = S_W_IDLE;
                end
            end
        endcase
    end

    //----------------------------------------------------------
    // read channel (AR, R)
    //----------------------------------------------------------
    localparam logic [1:0]      S_R_IDLE = 0,
                                S_R_ARREADY = 1,
                                S_R_DELAY = 2,
                                S_R_BURST = 3;

    logic   [1:0]               rstate,             rstate_n;
    logic   [7:0]               rcnt,               rcnt_n;

    logic   [ADDR_WIDTH-1:0]    raddr,              raddr_n;
    logic   [ID_WIDTH-1:0]      rid,                rid_n;
    logic   [3:0]               rlen,               rlen_n;

    always_ff @(posedge clk)
        if (!rst_n) begin
            rstate              <= S_R_IDLE;

            rcnt                <= 8'd0;
            raddr               <= {ADDR_WIDTH{1'b0}};
            rid                 <= {ID_WIDTH{1'b0}};
            rlen                <= 4'd0;
        end
        else begin
            rstate              <= rstate_n;

            rcnt                <= rcnt_n;
            raddr               <= raddr_n;
            rid                 <= rid_n;
            rlen                <= rlen_n;
        end

    always_comb begin
        rstate_n                = rstate;

        rcnt_n                  = rcnt;
        raddr_n                 = raddr;
        rid_n                   = rid;
        rlen_n                  = rlen;

        ar_ch.arready           = 1'b0;
        r_ch.rvalid             = 1'b0;
        r_ch.rlast              = 1'b0;

        case (rstate)
            S_R_IDLE: begin
                if (ar_ch.arvalid) begin
                    if (ARREADY_DELAY == 0) begin
                        raddr_n                 = ar_ch.araddr;
                        rid_n                   = ar_ch.arid;
                        rlen_n                  = ar_ch.arlen;
                        ar_ch.arready           = 1'b1;

                        rcnt_n                  = AR2R_DELAY - 1;
                        rstate_n                = S_R_DELAY;
                    end
                    else begin
                        rcnt_n                  = ARREADY_DELAY-1;
                        rstate_n                = S_R_ARREADY;
                    end
                end
            end
            S_R_ARREADY: begin
                if (rcnt==0) begin
                    raddr_n                 = ar_ch.araddr;
                    rid_n                   = ar_ch.arid;
                    rlen_n                  = ar_ch.arlen;
                    ar_ch.arready           = 1'b1;

                    rcnt_n                  = AR2R_DELAY - 1;
                    rstate_n                = S_R_DELAY;
                end
                else begin
                    rcnt_n                  = rcnt - 8'd1;
                end
            end
            S_R_DELAY: begin
                if (rcnt==0) begin
                    rstate_n                = S_R_BURST;
                end
                else begin
                    rcnt_n                  = rcnt - 8'd1;
                end
            end
            S_R_BURST: begin
                r_ch.rvalid             = 1'b1;
                r_ch.rlast              = (rlen==4'd0);
                for (int i=0; i<DATA_WIDTH/8; i++) begin
                    r_ch.rdata[i*8 +: 8] = read_byte(raddr + i);    // [i*8+7:i*8]
                end
                if (r_ch.rready) begin
                    raddr_n             = raddr + (DATA_WIDTH/8);
                    if (rlen==4'd0) begin
                        rstate_n                = S_R_IDLE;
                    end
                    else begin
                        rlen_n              = rlen - 4'd1;
                    end
                end
            end
        endcase
    end

    // output assignments
    assign  b_ch.bid            = wid;
    assign  b_ch.bresp          = 2'd0;
    assign  r_ch.rid            = rid;
    assign  r_ch.rresp          = 2'd0;

endmodule
