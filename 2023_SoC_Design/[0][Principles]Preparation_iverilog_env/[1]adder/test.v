
`timescale 1ns/1ps     //`timescale timeunit/timeresolution
module test;

reg [7:0] a, b; 
wire[7:0] y;

// for 'test_adder.vcd' to be saved as a file, a.out ELF must be executed
initial 
begin
    $dumpfile("./test_adder.vcd");
    // dump level 0 : all variables contained in modules of the designated module  
    // dump level 1 : variables for the designated module
    // dump level 2 : variables for the designated module and for the ones in a lower hierarchy
    $dumpvars(0, test);
end

initial  
begin  
    a = 4; 
    b = 2; 
    #10;
    $display("A=%d, B=%d, Y=%d", a,b,y);

    a = 6; 
    b = 3; 
    #10;
    $display("A=%d, B=%d, Y=%d", a,b,y);

    $finish(); 
end

// instantiation
adder u_adder ( 
    // port mapping (named mapping style)    
    .A(a), 
    .B(b), 
    .Y(y)
); 
endmodule
