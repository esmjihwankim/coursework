// Copyright (c) 2021 Sungkyunkwan University
//
// Authors:
// - Jungrae Kim <dale40@skku.edu>
// - Jihwan Kim

module DMAC_TOP
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

    // AMBA AXI interface (AW channel)
    output  wire    [3:0]       awid_o,
    output  wire    [31:0]      awaddr_o,
    output  wire    [3:0]       awlen_o,
    output  wire    [2:0]       awsize_o,
    output  wire    [1:0]       awburst_o,
    output  wire                awvalid_o,
    input   wire                awready_i,

    // AMBA AXI interface (AW channel)
    output  wire    [3:0]       wid_o,
    output  wire    [31:0]      wdata_o,
    output  wire    [3:0]       wstrb_o,
    output  wire                wlast_o,
    output  wire                wvalid_o,
    input   wire                wready_i,

    // AMBA AXI interface (B channel)
    input   wire    [3:0]       bid_i,
    input   wire    [1:0]       bresp_i,
    input   wire                bvalid_i,
    output  wire                bready_o,

    // AMBA AXI interface (AR channel)
    output  wire    [3:0]       arid_o,
    output  wire    [31:0]      araddr_o,
    output  wire    [3:0]       arlen_o,
    output  wire    [2:0]       arsize_o,
    output  wire    [1:0]       arburst_o,
    output  wire                arvalid_o,
    input   wire                arready_i,

    // AMBA AXI interface (R channel)
    input   wire    [3:0]       rid_i,
    input   wire    [31:0]      rdata_i,
    input   wire    [1:0]       rresp_i,
    input   wire                rlast_i,
    input   wire                rvalid_i,
    output  wire                rready_o
);
    localparam                  N_CH    = 4;

    wire    [31:0]              src_addr_vec[N_CH];
    wire    [31:0]              dst_addr_vec[N_CH];
    wire    [15:0]              byte_len_vec[N_CH];
    wire                        start_vec[N_CH];
    wire                        done_vec[N_CH];

    wire    [3:0]               awid_vec[N_CH];
    wire    [31:0]              awaddr_vec[N_CH];
    wire    [3:0]               awlen_vec[N_CH];
    wire    [2:0]               awsize_vec[N_CH];
    wire    [1:0]               awburst_vec[N_CH];
    wire                        awvalid_vec[N_CH];
    wire                        awready_vec[N_CH];

    wire    [3:0]               wid_vec[N_CH];
    wire    [31:0]              wdata_vec[N_CH];
    wire    [3:0]               wstrb_vec[N_CH];
    wire                        wlast_vec[N_CH];
    wire                        wvalid_vec[N_CH];
    wire                        wready_vec[N_CH];
    wire                        bready_vec[N_CH];
    wire    [3:0]               arid_vec[N_CH];
    wire    [31:0]              araddr_vec[N_CH];
    wire    [3:0]               arlen_vec[N_CH];
    wire    [2:0]               arsize_vec[N_CH];
    wire    [1:0]               arburst_vec[N_CH];
    wire                        arvalid_vec[N_CH];
    wire                        arready_vec[N_CH];
    wire                        rready_vec[N_CH];

    DMAC_CFG u_cfg(
        .clk                    (clk),
        .rst_n                  (rst_n),

        // AMBA APB interface
        .psel_i                 (psel_i),
        .penable_i              (penable_i),
        .paddr_i                (paddr_i),
        .pwrite_i               (pwrite_i),
        .pwdata_i               (pwdata_i),
        .pready_o               (pready_o),
        .prdata_o               (prdata_o),

        .ch0_src_addr_o     	(src_addr_vec[0]),
        .ch0_dst_addr_o	        (dst_addr_vec[0]),
        .ch0_byte_len_o     	(byte_len_vec[0]),
        .ch0_start_o    		(start_vec[0]),
        .ch0_done_i         	(done_vec[0]),

        .ch1_src_addr_o     	(src_addr_vec[1]),
        .ch1_dst_addr_o	        (dst_addr_vec[1]),
        .ch1_byte_len_o     	(byte_len_vec[1]),
        .ch1_start_o    		(start_vec[1]),
        .ch1_done_i         	(done_vec[1]),

        .ch2_src_addr_o     	(src_addr_vec[2]),
        .ch2_dst_addr_o	        (dst_addr_vec[2]),
        .ch2_byte_len_o     	(byte_len_vec[2]),
        .ch2_start_o    		(start_vec[2]),
        .ch2_done_i         	(done_vec[2]),

        .ch3_src_addr_o     	(src_addr_vec[3]),
        .ch3_dst_addr_o	        (dst_addr_vec[3]),
        .ch3_byte_len_o     	(byte_len_vec[3]),
        .ch3_start_o    		(start_vec[3]),
        .ch3_done_i         	(done_vec[3])
    );

	assign	pslverr_o			= 1'b0;

    DMAC_ARBITER #(
        .N_MASTER               (N_CH),
        .DATA_SIZE              ($bits(arid_o)+$bits(araddr_o)+$bits(arlen_o)+$bits(arsize_o)+$bits(arburst_o))
    )
    u_ar_arbiter
    (
        .clk                    (clk),
        .rst_n                  (rst_n),

        .src_valid_i            (arvalid_vec),
        .src_ready_o            (arready_vec),
        .src_data_i             ({
                                  {arid_vec[0], araddr_vec[0], arlen_vec[0], arsize_vec[0], arburst_vec[0]},
                                  {arid_vec[1], araddr_vec[1], arlen_vec[1], arsize_vec[1], arburst_vec[1]},
                                  {arid_vec[2], araddr_vec[2], arlen_vec[2], arsize_vec[2], arburst_vec[2]},
                                  {arid_vec[3], araddr_vec[3], arlen_vec[3], arsize_vec[3], arburst_vec[3]}}),

        .dst_valid_o            (arvalid_o),
        .dst_ready_i            (arready_i),
        .dst_data_o             ({arid_o, araddr_o, arlen_o, arsize_o, arburst_o})
    );

    DMAC_ARBITER #(
        .N_MASTER               (N_CH),
        .DATA_SIZE              ($bits(awid_o)+$bits(awaddr_o)+$bits(awlen_o)+$bits(awsize_o)+$bits(awburst_o))
    )
    u_aw_arbiter
    (
        .clk                    (clk),
        .rst_n                  (rst_n),

        .src_valid_i            (awvalid_vec),
        .src_ready_o            (awready_vec),
        .src_data_i             ({
                                  {awid_vec[0], awaddr_vec[0], awlen_vec[0], awsize_vec[0], awburst_vec[0]},
                                  {awid_vec[1], awaddr_vec[1], awlen_vec[1], awsize_vec[1], awburst_vec[1]},
                                  {awid_vec[2], awaddr_vec[2], awlen_vec[2], awsize_vec[2], awburst_vec[2]},
                                  {awid_vec[3], awaddr_vec[3], awlen_vec[3], awsize_vec[3], awburst_vec[3]}}),

        .dst_valid_o            (awvalid_o),
        .dst_ready_i            (awready_i),
        .dst_data_o             ({awid_o, awaddr_o, awlen_o, awsize_o, awburst_o})
    );

    DMAC_ARBITER #(
        .N_MASTER               (N_CH),
        .DATA_SIZE              ($bits(wid_o)+$bits(wdata_o)+$bits(wstrb_o)+$bits(wlast_o))
    )
    u_w_arbiter
    (
        .clk                    (clk),
        .rst_n                  (rst_n),

        .src_valid_i            (wvalid_vec),
        .src_ready_o            (wready_vec),
        .src_data_i             ({
                                  {wid_vec[0], wdata_vec[0], wstrb_vec[0], wlast_vec[0]},
                                  {wid_vec[1], wdata_vec[1], wstrb_vec[1], wlast_vec[1]},
                                  {wid_vec[2], wdata_vec[2], wstrb_vec[2], wlast_vec[2]},
                                  {wid_vec[3], wdata_vec[3], wstrb_vec[3], wlast_vec[3]}}),

        .dst_valid_o            (wvalid_o),
        .dst_ready_i            (wready_i),
        .dst_data_o             ({wid_o, wdata_o, wstrb_o, wlast_o})
    );

    assign  bready_o                = (bid_i=='d0) ? bready_vec[0] :
                                      (bid_i=='d1) ? bready_vec[1] :
                                      (bid_i=='d2) ? bready_vec[2] :
                                                     bready_vec[3];

    assign  rready_o                = (rid_i=='d0) ? rready_vec[0] :
                                      (rid_i=='d1) ? rready_vec[1] :
                                      (rid_i=='d2) ? rready_vec[2] :
                                                     rready_vec[3];

    genvar ch;
    generate
        for (ch=0; ch<N_CH; ch++) begin: channel
            DMAC_ENGINE u_engine(
                .clk                    (clk),
                .rst_n                  (rst_n),
        
                // configuration registers
                .src_addr_i             (src_addr_vec[ch]),
                .dst_addr_i             (dst_addr_vec[ch]),
                .byte_len_i             (byte_len_vec[ch]),
                .start_i                (start_vec[ch]),
                .done_o                 (done_vec[ch]),
        
                // AMBA AXI interface (AW channel)
                .awaddr_o               (awaddr_vec[ch]),
                .awlen_o                (awlen_vec[ch]),
                .awsize_o               (awsize_vec[ch]),
                .awburst_o              (awburst_vec[ch]),
                .awvalid_o              (awvalid_vec[ch]),
                .awready_i              (awready_vec[ch]),
        
                // AMBA AXI interface (W channel)
                .wdata_o                (wdata_vec[ch]),
                .wstrb_o                (wstrb_vec[ch]),
                .wlast_o                (wlast_vec[ch]),
                .wvalid_o               (wvalid_vec[ch]),
                .wready_i               (wready_vec[ch]),
        
                // AMBA AXI interface (B channel)
                .bresp_i                (bresp_i),
                .bvalid_i               (bvalid_i & (bid_i==ch)),
                .bready_o               (bready_vec[ch]),
        
                // AMBA AXI interface (AR channel)
                .araddr_o               (araddr_vec[ch]),
                .arlen_o                (arlen_vec[ch]),
                .arsize_o               (arsize_vec[ch]),
                .arburst_o              (arburst_vec[ch]),
                .arvalid_o              (arvalid_vec[ch]),
                .arready_i              (arready_vec[ch]),
        
                // AMBA AXI interface (R channel)
                .rdata_i                (rdata_i),
                .rresp_i                (rresp_i),
                .rlast_i                (rlast_i),
                .rvalid_i               (rvalid_i & (rid_i==ch)),
                .rready_o               (rready_vec[ch])
            );

            assign  awid_vec[ch]        = ch;
            assign  wid_vec[ch]         = ch;
            assign  arid_vec[ch]        = ch;
        end
    endgenerate

endmodule
