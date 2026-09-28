`timescale 1ns/1ps

module powereight_test; 

reg clk, reset_n; 
reg        i_valid; 
reg   [31:0]  ivalue; 
wire       o_valid; 
wire  [63:0]  o_power_of_8; 

// clk generation 
always 
    #5 clk = ~clk;

integer i;
integer fd; 

initial begin 
//initialize value 
    $display("initialize value [%d]", $time); 
    reset_n = 1; 
    clk = 0; 
    i_valid = 0; 
    i_value = 0; 
    fd = $fopen("rtl_v.text", "w");

    // reset_n gen 
    $display("Reset! [%d]", $time); 
    #100
    reset_n = 0; 
    #10
    reset_n = 1; 
    #10 
    @(posedge clk); 
    $display("Start! [%d]", $time); 
    for(i = 0; i < 100; i = i+1) begin
        @(negedge clk); 
        i_valid = 1; 
        i_value = i; 
        @(posedge clk); 
    end
    @(negedge clk); 
    i_valid = 0; 
    i_value = 0; 
    
    #100
    $display("Finish! [%d]", $time); 
    $fclose(fd);
    $finish; 
end 


// file write 
always @(posedge clk) begin 
    if(o_valid) begin 
        $fwrite(fd, "result = %0d\n", o_power_of_8);
    end
end

// call DUT 
powereight u_powereight(
    .clk(clk),
    .reset_n(reset_n),
    .ivalue(ivalue),
    .o_valid(o_valid),
    .o_power_of_8(o_power_of_8)
); 

endmodule
