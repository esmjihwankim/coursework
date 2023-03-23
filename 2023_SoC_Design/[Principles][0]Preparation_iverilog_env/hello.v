module adder
(
    // where you declare the input and output
    // the syntax format follows...
    // in/out keyword - (data type) [bit range] (variable name)
    input   wire [7:0] A,       // 8 bit input port
    input   wire [7:0] B,       // 8 bit input port
    output  wire [7:0] Y        // 8 bit output port
); 
// where you implement the functionality 

// wire type requires assign keyword
wire [7:0] sum; 
assign sum = A + B; 

// register type requires begin/end block 
// signals for the sensitivity list after '@ is separated by 'or' 
reg [7:0] sum; 
always @(A or B)
begin 
    sum = A+B; 
end 

// Y port requires assign keyword because it's a wire
assign Y = sum; 




// number representation 
// (digit)'(radix)(number)


endmodule