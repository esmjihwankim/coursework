module barrel_shifter (
	input clock,
    input resetn,
	input [7:0] a,
    input [2:0] num,
    input left_right,
    output reg [7:0] y
    );
    
reg [7:0] result;
 
task shifter (input [7:0] a, input [2:0] num, input left_right, output [7:0] y);
begin
    if (left_right == 0) 
    	y = #1 a >> num;
    else
    	y = #1 a << num;
end
endtask
 
always @(posedge clock or negedge resetn)
begin
    if (~resetn)
    	y <= 0;
    else
    begin
    	shifter(a, num, left_right, result);
    	y <= result;
    end
end
    
endmodule