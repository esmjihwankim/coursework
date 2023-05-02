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
    
    localparam      S_IDLE = 3'd0,
                    S_READ = 3'd1,
                    S_WREQ = 3'd2,
                    S_WRITE = 3'd3;

    /*
     *  register update for each clock 
     */ 
    reg [2:0] state, state_n; 
    always_ff @(posedge clk) begin
        if(!rst_n) begin 
            state   <= S_IDLE;
        end
        else begin
            state   <= state_n;
        end
    end

    /* 
     *   Finite State Machine
     */ 
    reg[2:0] i, j, k, m, n; 
    reg [DATA_SIZE-1:0] buffer[N_MASTER];
    reg buffer_full[N_MASTER];

    always_comb begin
        state_n = state; 
        case(state) 
            S_IDLE: begin    // take in valid input first into the buffer 
                for(i=0; i<N_MASTER; i=i+1) begin
                    if(src_valid_i[i]) begin
                        buffer[i] = src_data_i[i];    // fill data into buffer
                        buffer_full[i] = 1'b1;    // mark buffer as full 
                        state_n = S_READ;
                    end else begin   // stay in the state
                        buffer_full[i] = 1'b0;  
                    end
                end
            end
            // OUTPUT:: src_ready_o = 1
            S_READ: begin    // signals ready to receive and fill buffers
                for(j=0; j<N_MASTER; j=j+1) begin
                    if(src_valid_i[j]) begin
                        src_ready_o[j] = 1'b1;
                    end
                end
                state_n = S_WREQ;
            end
            // signals ready to send
            S_WREQ: begin    // OUTPUT:: src_ready_o = 0, dst_valid_o = 1
                for(k=0; k<N_MASTER; k=k+1) begin    // ready 
                    src_ready_o[k] = 1'b0;
                    if(buffer_full[k]) begin
                        dst_valid_o = 1'b1;
                        state_n = S_WRITE;
                    end else begin
                    end
                end
            end
            // send everything sequentially 
            S_WRITE: begin // OUTPUT:: 
                if(buffer_full[0] && dst_valid_o && dst_ready_i) begin
                    dst_data_o = buffer[0]; 
                    buffer_full[0] = 1'b0;
                end else if(buffer_full[1] && dst_valid_o && dst_ready_i) begin
                    dst_data_o = buffer[1];
                    buffer_full[1] = 1'b0;
                end else if(buffer_full[2] && dst_valid_o && dst_ready_i) begin
                    dst_data_o = buffer[2];
                    buffer_full[2] = 1'b0;
                end else if(buffer_full[3] && dst_valid_o && dst_ready_i) begin
                    dst_data_o = buffer[3];
                    buffer_full[3] = 1'b0;
                end else begin
                end

                if(!buffer_full[0] && !buffer_full[1] && !buffer_full[2] && !buffer_full[3]) begin
                    state_n = S_IDLE;
                end else begin
                end
            end

        endcase 
    end 
endmodule

