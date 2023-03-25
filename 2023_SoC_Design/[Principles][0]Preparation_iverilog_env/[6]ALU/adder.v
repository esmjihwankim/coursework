module adder(
    input clock,
    input resetn, 
    input [7:0] a,
    input [7:0] b, 
    output reg [7:0] y
);

reg [7:0] sum; 

always@(*)
begin 
    sum = a + b; 
end

always @(posedge clock or negedge resetn)
begin 
    if(!resetn)
        y <= 0; 
    else 
        y <= sum; 
end 
endmodule