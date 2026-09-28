
module regfile (
    input wire CLK,
    input wire RSTn,
    input wire [1:0] ADDR, 
    input wire WE,
    input wire [3:0] DIN,
    output reg [3:0] DOUT
);

reg [3:0] reg_din [0:3];
reg [3:0] mem [0:3];
wire [3:0] reg_dout [0:3];

// demux for choosing the lane on which the data flow
always@(*)
begin
    case(ADDR)
    2'b00:
        reg_din[0] = DIN;
    2'b01:
        reg_din[1] = DIN; 
    2'b10:
        reg_din[2] = DIN;
    2'b11:
        reg_din[3] = DIN;
    default:
    begin
        reg_din[0] = 0;
        reg_din[1] = 0;
        reg_din[2] = 0;
        reg_din[3] = 0;
    end
endcase
end

// mux for choosing the output data - refers to ADDR 
always@(*)
begin
    case(ADDR)
        2'b00:
        DOUT = reg_dout[0];
        2'b01:
        DOUT = reg_dout[1];
        2'b10:
        DOUT = reg_dout[2];
        2'b11:
        DOUT = reg_dout[3]; 
        default:
            DOUT = 0;
    endcase
end

always @(posedge CLK or negedge RSTn)
begin
    if(!RSTn)
        mem[0] <= 0;
    else if (WE & (ADDR == 2'b00))
        mem[0] <= reg_din[0]; 
end
assign reg_dout[0] = mem[0]; 

always @(posedge CLK or negedge RSTn)
begin
    if(!RSTn)
        mem[1] <= 0;
    else if(WE & (ADDR == 2'b01))
        mem[1] <= reg_din[1];
end
assign reg_dout[1] = mem[1];

always @(posedge CLK or negedge RSTn)
begin
    if(!RSTn)
        mem[2] <= 0; 
    else if(WE & (ADDR == 2'b10))
        mem[2] <= reg_din[2];
end 
assign reg_dout[2] = mem[2]; 

always @(posedge CLK or negedge RSTn)
begin
    if(!RSTn)
        mem[3] <= 0; 
    else if (WE & (ADDR == 2'b11))
        mem[3] <= reg_din[3];
end
assign reg_dout[3] = mem[3];
endmodule