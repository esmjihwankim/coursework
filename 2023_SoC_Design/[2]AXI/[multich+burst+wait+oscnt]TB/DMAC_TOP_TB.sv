`define     IP_VER      32'h000
`define     CH_SFR_SIZE 32'h100
`define     SRC_OFFSET  32'h0
`define     DST_OFFSET  32'h4
`define     LEN_OFFSET  32'h8
`define     CMD_OFFSET  32'hc
`define     STAT_OFFSET 32'h10

`define 	  TIMEOUT_DELAY 	99999999

`define     SRC_REGION_START    32'h0000_0000
`define     SRC_REGION_SIZE     32'h0000_2000
`define     DST_REGION_STRIDE   32'h0000_2000

`define     RANDOM_SEED     12123344
`define     TEST_CNT        100

module DMAC_TOP_TB ();

    // inject random seed
    initial begin
        $srandom(`RANDOM_SEED);
    end

    //----------------------------------------------------------
    // clock and reset generation
    //----------------------------------------------------------
    reg                     clk;
    reg                     rst_n;

    reg [3:0]               data1, data2;
    initial begin
        data1 = 'b101x;
        data2 = 'b1010;
        $display("Result: %d %d", data1===data2, data1!==data2);
        $display("Result: %d %d", data1==data2, data1!=data2);
        data1 = 'b101x;
        data2 = 'b101x;
        $display("Result: %d", data1===data2);
        $display("Result: %d", data1==data2);
    end

    // clock generation
    initial begin
        clk                     = 1'b0;

        forever #10 clk         = !clk;
    end

    // reset generation
    initial begin
        rst_n                   = 1'b0;     // active at time 0

        repeat (3) @(posedge clk);          // after 3 cycles,
        rst_n                   = 1'b1;     // release the reset
    end

	// timeout
	initial begin
		#`TIMEOUT_DELAY $display("Timeout!");
		$finish;
	end

    // enable waveform dump
    initial begin
        $dumpvars(0, u_DUT);
        $dumpfile("dump.vcd");
    end

    //----------------------------------------------------------
    // Connection between DUT and test modules
    //----------------------------------------------------------
    APB                         apb_if  (.clk(clk));

    AXI_AW_CH                   aw_ch   (.clk(clk));
    AXI_W_CH                    w_ch    (.clk(clk));
    AXI_B_CH                    b_ch    (.clk(clk));
    AXI_AR_CH                   ar_ch   (.clk(clk));
    AXI_R_CH                    r_ch    (.clk(clk));

    DMAC_TOP  u_DUT (
        .clk                    (clk),
        .rst_n                  (rst_n),

        // APB interface
        .psel_i                 (apb_if.psel),
        .penable_i              (apb_if.penable),
        .paddr_i                (apb_if.paddr[11:0]),
        .pwrite_i               (apb_if.pwrite),
        .pwdata_i               (apb_if.pwdata),
        .pready_o               (apb_if.pready),
        .prdata_o               (apb_if.prdata),
        .pslverr_o              (apb_if.pslverr),

        // AXI AW channel
        .awid_o                 (aw_ch.awid),
        .awaddr_o               (aw_ch.awaddr),
        .awlen_o                (aw_ch.awlen),
        .awsize_o               (aw_ch.awsize),
        .awburst_o              (aw_ch.awburst),
        .awvalid_o              (aw_ch.awvalid),
        .awready_i              (aw_ch.awready),

        // AXI W channel
        .wid_o                  (w_ch.wid),
        .wdata_o                (w_ch.wdata),
        .wstrb_o                (w_ch.wstrb),
        .wlast_o                (w_ch.wlast),
        .wvalid_o               (w_ch.wvalid),
        .wready_i               (w_ch.wready),

        // AXI B channel
        .bid_i                  (b_ch.bid),
        .bresp_i                (b_ch.bresp),
        .bvalid_i               (b_ch.bvalid),
        .bready_o               (b_ch.bready),

        // AXI AR channel
        .arid_o                 (ar_ch.arid),
        .araddr_o               (ar_ch.araddr),
        .arlen_o                (ar_ch.arlen),
        .arsize_o               (ar_ch.arsize),
        .arburst_o              (ar_ch.arburst),
        .arvalid_o              (ar_ch.arvalid),
        .arready_i              (ar_ch.arready),

        // AXI R channel
        .rid_i                  (r_ch.rid),
        .rdata_i                (r_ch.rdata),
        .rresp_i                (r_ch.rresp),
        .rlast_i                (r_ch.rlast),
        .rvalid_i               (r_ch.rvalid),
        .rready_o               (r_ch.rready)
    );

    AXI_SLAVE   u_mem (
        .clk                    (clk),
        .rst_n                  (rst_n),

        .aw_ch                  (aw_ch),
        .w_ch                   (w_ch),
        .b_ch                   (b_ch),
        .ar_ch                  (ar_ch),
        .r_ch                   (r_ch)
    );

    //----------------------------------------------------------
    // Testbench starts
    //----------------------------------------------------------
    task test_init();
        int data;
        apb_if.init();

        @(posedge rst_n);                   // wait for a release of the reset
        repeat (10) @(posedge clk);         // wait another 10 cycles

        apb_if.read(`IP_VER, data);
        $display("---------------------------------------------------");
        $display("IP version: %x", data);
        $display("---------------------------------------------------");

        $display("---------------------------------------------------");
        $display("Load data to memory");
        $display("---------------------------------------------------");
        for (int i=0; i<`SRC_REGION_SIZE; i=i+4) begin
            // write random data
            u_mem.write_word(`SRC_REGION_START+i, $random);
        end
    endtask

    // this task must be declared automatic so that each invocation uses
    // different memories
    task automatic test_dma(input int ch, input int src, input int dst, input int len);
        int data;
        $display("Ch[%d] DMA configure %x -> %x (%x)", ch, src, dst, len);
        apb_if.write((ch+1)*`CH_SFR_SIZE+`SRC_OFFSET, src);
        apb_if.read((ch+1)*`CH_SFR_SIZE+`SRC_OFFSET, data);
        if (data!==src) begin
            $display("DMA_SRC[%d](fail): %x", ch, data);
            @(posedge clk);
            $finish;
        end
        apb_if.write((ch+1)*`CH_SFR_SIZE+`DST_OFFSET, dst);
        apb_if.read((ch+1)*`CH_SFR_SIZE+`DST_OFFSET, data);
        if (data!==dst) begin
            $display("DMA_DST[%d](fail): %x", ch, data);
            @(posedge clk);
            $finish;
        end
        apb_if.write((ch+1)*`CH_SFR_SIZE+`LEN_OFFSET, len);
        apb_if.read((ch+1)*`CH_SFR_SIZE+`LEN_OFFSET, data);
        if (data!==len) begin
            $display("DMA_LEN[%d](fail): %x", ch, data);
            @(posedge clk);
            $finish;
        end

        $display("Ch[%d] DMA start", ch);
        apb_if.write((ch+1)*`CH_SFR_SIZE+`CMD_OFFSET, 32'h1);

        data = 0;
        while (data!=1) begin
            apb_if.read((ch+1)*`CH_SFR_SIZE+`STAT_OFFSET, data);
            repeat (100) @(posedge clk);
            $display("Ch[%d] Waiting for a DMA completion", ch);
        end
        @(posedge clk);

        $display("Ch[%d] DMA completed", ch);
        for (int i=0; i<len; i=i+4) begin
            logic [31:0]        src_word;
            logic [31:0]        dst_word;
            src_word            = u_mem.read_word(src+i);
            dst_word            = u_mem.read_word(dst+i);
            if (src_word!==dst_word) begin
                $display("Ch[%d] Mismatch! (src:%x @%x, dst:%x @%x", ch, src_word, src+i, dst_word, dst+i);
                @(posedge clk);
                $finish;
            end
        end
        $display("Ch[%d] DMA passed", ch);
    endtask

    // this task must be declared automatic so that each invocation uses
    // different memories
    task automatic test_channel(input int ch, input int test_cnt);
        int         src_offset, dst_offset, len;
        src_offset = 0;
        dst_offset = 0;

        for (int i=0; i<test_cnt; i++) begin
            len = 'h0100;
            test_dma(ch, `SRC_REGION_START+src_offset, (ch+1)*`DST_REGION_STRIDE+dst_offset, len);
            src_offset = src_offset + len;
            dst_offset = dst_offset + len;
        end
    endtask


    // main
    initial begin
        test_init();

        // run 4 channel tests simultaneously
        fork
            test_channel(0, `TEST_CNT);
            test_channel(1, `TEST_CNT);
            test_channel(2, `TEST_CNT);
            test_channel(3, `TEST_CNT);
        join

        $finish;
    end


endmodule
