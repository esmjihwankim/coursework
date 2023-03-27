module subtractor (
    input                   clock, 
    input                   resetn,
    input                   en,
    input   wire [7:0]      a,     
    input   wire [7:0]      b,
    output  reg  [7:0]      y
);

function [7:0] sub (input [7:0] a, input [7:0] b);
begin 
    sub = a - b; 
end 
endfunction

always @(posedge clock or negedge resetn)
begin 
    if(~resetn)
        y <= 0;
    else if (en)
        y <= sub(a,b); 
end 
endmodule
