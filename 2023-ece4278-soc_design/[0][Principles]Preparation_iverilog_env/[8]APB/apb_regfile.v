
module apb_regfile #(
    parameter ADDR_WIDTH=8,
    parameter DATA_WIDTH=16
)
(
    input wire PCLK,
    input wire PRESETn,
    input wire [ADDR_WIDTH-1:0] PADDR,
    input wire PSEL,
    input wire PENABLE,
    input wire PWRITE,
    input wire [DATA_WIDTH-1:0] PWDATA,
    output reg [DATA_WIDTH-1:0] PRDATA,
    output wire PREADY
);


// APB has 3 states 
parameter IDLE = 2'b00; 
parameter SETUP = 2'b01;
parameter ACCESS = 2'b10; 

reg [1:0] curr_state; 
reg [1:0] next_state; 

wire [ADDR_WIDTH-1:0] ADDR;
wire [DATA_WIDTH-1:0] DIN;
wire [DATA_WIDTH-1:0] DOUT;
wire                  WE; 

always @(posedge clk or negedge rstn)
begin
    if(~rstn)
        curr_state <= IDLE; 
    else 
        curr_state <= next_state; 
end

// determination of the next state 
// refer to the state diagram and produce code
always @(*)
begin
    // case statement implemented with combinational logic -> default statement is required 
    case(curr_state)
        IDLE:
            if(PSEL == 1)
                next_state = SETUP;
            else 
                next_state = curr_state; 
        SETUP:
            if(PENABLE == 1)
                next_state = ACCESS;
            else 
                next_state = curr_state
        ACCESS:
            if(PSEL == 0 && PENABLE == 0 && PREADY == 1)
                next_state = IDLE;
            else if(PSEL == 1 && PREADY == 1)
                next_state = SETUP;
            else
                next_state = curr_state;
        default:
            next_state = IDLE;
    endcase
end


// register file
assign ADDR = PADDR;
assign DIN = PWDATA;
assign PREADV = 1;
assign WE = (next_state == ACCESS) & PWRITE;

always @(*) PRDATA = DOUT; 

regfile #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .DATA_WIDTH(DATA_WIDTH),
) u_regfile (
    .clk(PCLK),
    .rst_n(PRESETn),
    .ADDR(ADDR),
    .DIN(DIN),
    .DOUT(DOUT),
    .WE(WE)
);
endmodule