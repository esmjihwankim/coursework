module DMAC_ARBITER
#(
    N_MASTER                    = 4,
    DATA_SIZE                   = 32
)
(
    input   wire                clk,
    input   wire                rst_n,  // _n means active low

    // configuration registers
    input   wire                        src_valid_i[N_MASTER],    // arrives at 1290000ps
    output  reg                         src_ready_o[N_MASTER],
    input   wire    [DATA_SIZE-1:0]     src_data_i[N_MASTER],

    output  reg                     dst_valid_o,
    input   wire                    dst_ready_i,
    output  reg     [DATA_SIZE-1:0] dst_data_o
);          
    
    localparam      S_READ     = 3'd0,
                    S_RDCK     = 3'd1,
                    S_WREQ     = 3'd2,
                    S_WRITE    = 3'd3;

    /*
     *  register update for each clock 
     */ 
    reg [3:0] state, state_n; 
    always_ff @(posedge clk) begin
        if(!rst_n) begin 
            state   <= S_READ;
        end
        else begin
            state   <= state_n;
        end
    end

    /* 
     *   Finite State Machine
     */ 
    reg[2:0] choose_ch;
    reg[2:0] i, j, k, m, n; 
    reg [DATA_SIZE-1:0] buffer;
    reg buffer_full[N_MASTER];

    always_comb begin
        state_n = state; 
        case(state) 
            // READ STATE:::takes in valid input first into the buffer 
            S_READ: begin   
                if(src_valid_i[0]) begin
                    buffer = src_data_i[0]; 
                    choose_ch = 3'd0;
                end else if (src_valid_i[1]) begin
                    buffer = src_data_i[1];
                    choose_ch = 3'd1;
                end else if (src_valid_i[2]) begin
                    buffer = src_data_i[2];
                    choose_ch = 3'd2; 
                end else if (src_valid_i[3]) begin
                    buffer = src_data_i[3]; 
                    choose_ch = 3'd3;
                end else begin 
                end
                if(src_valid_i[0] || src_valid_i[1] || src_valid_i[2] || src_valid_i[3]) begin
                    state_n = S_RDCK;
                end else begin
                end
                
            end
            // READCHECK STATE:::signals ready to receive and fill buffers 
            S_RDCK: begin 
                src_ready_o[choose_ch] = 1'b1;
                state_n = S_WREQ;
            end
            // WRITE REQUEST STATE::: drives data and valid to signal that data can be sent
            S_WREQ: begin    // signals 
                src_ready_o[choose_ch] = 1'b0;
                dst_valid_o = 1'b1; 
                dst_data_o = buffer;
                state_n = S_WRITE;
            end
            // WRITE STATE::: data sent and data no longer valid. move back to first state
            S_WRITE: begin 
                if(dst_ready_i) begin
                    dst_valid_o = 1'b0;
                    state_n = S_READ; 
                end else begin
                end
            end    
        endcase 
    end 
endmodule

