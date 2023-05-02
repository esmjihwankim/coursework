module DMAC_ARBITER
#(
    N_MASTER                    = 4,
    DATA_SIZE                   = 32
)
(
    input   wire                clk,
    input   wire                rst_n,  // _n means active low

    // configuration registers
    input   wire                        src_valid_i[N_MASTER],
    output  reg                         src_ready_o[N_MASTER],
    input   wire    [DATA_SIZE-1:0]     src_data_i[N_MASTER],

    output  reg                     dst_valid_o,
    input   wire                    dst_ready_i,
    output  reg     [DATA_SIZE-1:0] dst_data_o
);          

    wire fifo_full[N_MASTER];
    wire fifo_wren[N_MASTER];
    wire [DATA_SIZE-1:0] fifo_wdata[N_MASTER]; 
    
    wire fifo_empty[N_MASTER];
    reg fifo_rden[N_MASTER]; 
    wire [DATA_SIZE-1:0] fifo_rdata[N_MASTER];

    reg [2:0] state, state_n;

    localparam        S_IDLE = 3'd0, 
                      S_READ = 3'd1;
    genvar ch; 
    generate 
        for(ch = 0; ch < 4; ch=ch+1) begin : dfifo
            DMAC_FIFO #(.DEPTH_LG2(8),
                        .DATA_WIDTH(DATA_SIZE))   u_fifo
            (
                .clk                        (clk),          //
                .rst_n                      (rst_n),       //

                .full_o                     (fifo_full[ch]),
                .wren_i                     (fifo_wren[ch]),
                .wdata_i                    (fifo_wdata[ch]),

                .empty_o                    (fifo_empty[ch]),
                .rden_i                     (fifo_rden[ch]),
                .rdata_o                    (fifo_rdata[ch])
            );
        end
    endgenerate

    /*
      [1] full, empty 신호를 통해서 만들어야 할것.
          (1) empty면 data를 내보낼 수 없는 상태.  --> dst_valid_o
          (2) full이면 data를 받을 수 없는건데.    --> src_ready_o


      [2] data를 받는 코드(src)
          (1) src_data를 fifo에 연결하고          

      [3] data를 보내는 코드 (dst)
      
          (1) r_data[0:3] 중에서 어떤 데이터를 dst_data_o에 할당할지
          (2) dst_valid_i를 high low로 할지.
          (3) dst_ready_o가 high일때만 data를 내보내면 된다.
        

    만들어야 할 output list
    output  reg                     src_ready_o[N_MASTER],
    output  reg                     dst_valid_o,
    output  reg     [DATA_SIZE-1:0] dst_data_o
    */
    
    reg [2:0] i;     // for-loop variable
    reg [1:0] cnt;   // FIFO counter
    reg [1:0] cnt_n; // FIFO_counter_next


    
    /**
     * [0] output block 
     */
    // [0]에 해당하는 always block
    
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            //  default value of variable
            
            dst_valid_o <= 1'b0;
            cnt <= 2'b0;
        end 
        else begin
            if (!dst_ready_i && dst_valid_o) begin
                 // data hold
            end else begin
                cnt = 2'b0;
                if (!fifo_empty[cnt]) begin
                    $display("data : %d", fifo_empty[cnt]);
                    // data를 꺼내야지
                    fifo_rden[cnt] <= 1'b1;
                    cnt_n <= cnt;
                    dst_valid_o <= 1'b1;
                end else if (!fifo_empty[cnt+1]) begin
                    fifo_rden[cnt+1] <= 1'b1;
                    cnt_n <= cnt+1;
                    dst_valid_o <= 1'b1;
                end else if (!fifo_empty[cnt+2]) begin
                    fifo_rden[cnt+2] <= 1'b1;
                        cnt_n <= cnt+2;
                        dst_valid_o <= 1'b1;
                end else if (!fifo_empty[cnt+3]) begin
                    fifo_rden[cnt+3] <= 1'b1;
                    cnt_n <= cnt+3;
                    dst_valid_o <= 1'b1;
                end else begin
                    dst_valid_o <= 1'b0;
                end
            end
        end
    end 
    

    // output assignment
    always_comb begin
        dst_data_o = fifo_rdata[cnt_n]; 
    end

    /**
     * [0] block end
     */

    reg [2:0] j;  
     
    always_comb begin           
        for (j = 0 ; j < N_MASTER ; j = j + 1) begin
            if (src_valid_i[j] == 1'b1) begin 
                if (fifo_full[j] == 1'b0) begin
                    src_ready_o[j] = 1'b1;
                end else begin
                    src_ready_o[j] = 1'b0;
                end
            end else begin 
                // do nothing 
            end
        end
    end
     
    assign fifo_wren[0] = src_ready_o[0] && src_valid_i[0];
    assign fifo_wren[1] = src_ready_o[1] && src_valid_i[1];
    assign fifo_wren[2] = src_ready_o[2] && src_valid_i[2];
    assign fifo_wren[3] = src_ready_o[3] && src_valid_i[3];

    assign fifo_wdata[0] = src_data_i[0];
    assign fifo_wdata[1] = src_data_i[1];
    assign fifo_wdata[2] = src_data_i[2];
    assign fifo_wdata[3] = src_data_i[3];

endmodule
