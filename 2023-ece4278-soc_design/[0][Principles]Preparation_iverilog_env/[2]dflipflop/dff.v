module dff(
    input clk,
    input resetn,
    input d,
    output reg q
);

// always statement is a basic building block for parallel execution
// for combinational circuits, use blocking statements
// for sequential circuits, use non-blocking statements
always @(posedge clk or negedge resetn)
begin
    if(!resetn) 
        q <= 0; 
    else 
        q <= d; 
    
end 
endmodule