`timescale 1ns/1ps

module powereight(
    input       clk,
    input       reset_n, 
    input       ivalid,
    input     [31:0]    ivalue,

    output      o_valid,
    output    [63:0]    o_power_of_8
); 

    // Type 
    reg [2:0]      r_valid; 
    reg [63:0]     r_power_of_2; 
    reg [63:0]     r_power_of_4; 
    reg [63:0]     r_power_of_8; 
    wire [63:0]    power_of_2; 
    wire [63:0]    power_of_4; 
    wire [64:0]    power_of_8; 

    // flow of valid 
    always @(posedge clk or negedge reset_n) begin 
        if(!reset_n) begin 
           r_valid <= 3'd0; 
        end else begin
           r_valid <= {r_valid[1:0], i_valid}; 
        end
    end

    // data buffer (f/f)
    always @(posedge clk or negedge reset_n) begin
        if(!reset_n) begin
            r_power_of_2 <= 64'd0; 
            r_power_of_4 <= 64'd0;
            r_power_of_8 <= 64'd0; 
        end else begin 
            r_power_of_2 <= power_of_2; 
            r_power_of_4 <= power_of_4; 
            r_power_of_8 <= power_of_8; 
        end
    end 

    // power operation 
    assign power_of_2 = i_value * i_value; 
    assign power_of_4 = r_power_of_2 * r_power_of_2; 
    assign power_of_8 = r_power_of_4 * r_power_of_4; 

    assign o_valid = r_valid[2];
    assign o_power_of_8 = r_power_of_8; 
    
endmodule
    
    