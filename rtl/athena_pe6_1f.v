module athena_pe6_1f(
input [31:0] x0_a,x0_b, input [3:0] opA0, output [31:0] outA0,
input [31:0] x1_a,x1_b, input [3:0] opA1, output [31:0] outA1,
input [31:0] x2_a,x2_b, input [3:0] opA2, output [31:0] outA2,
input [31:0] x3_a,x3_b, input [3:0] opA3, output [31:0] outA3,
input [31:0] x4_a,x4_b, input [3:0] opA4, output [31:0] outA4,
input [31:0] x5_a,x5_b, input [3:0] opA5, output [31:0] outA5,
input [31:0] b0_a,b0_b, input [3:0] opB0, input enB0, output [31:0] outB0,
input [2:0] sel_fuse, input use_fuse,
input [31:0] b1_a,b1_b, input [3:0] opB1, input enB1, output [31:0] outB1,
input [31:0] b2_a,b2_b, input [3:0] opB2, input enB2, output [31:0] outB2,
input [31:0] b3_a,b3_b, input [3:0] opB3, input enB3, output [31:0] outB3,
input [31:0] b4_a,b4_b, input [3:0] opB4, input enB4, output [31:0] outB4,
input [31:0] b5_a,b5_b, input [3:0] opB5, input enB5, output [31:0] outB5
);
wire [31:0] ia0=outA0;
wire [31:0] ib0=use_fuse?(sel_fuse==0 ? outA1 : sel_fuse==1 ? outA2 : sel_fuse==2 ? outA3 : sel_fuse==3 ? outA4 : outA5):b0_b;
wire [31:0] ia1=outA1;
wire [31:0] ib1=b1_b;
wire [31:0] ia2=outA2;
wire [31:0] ib2=b2_b;
wire [31:0] ia3=outA3;
wire [31:0] ib3=b3_b;
wire [31:0] ia4=outA4;
wire [31:0] ib4=b4_b;
wire [31:0] ia5=outA5;
wire [31:0] ib5=b5_b;
athena_alu32 ua0(.a(x0_a),.b(x0_b),.op(opA0),.y(outA0));
athena_alu32 ua1(.a(x1_a),.b(x1_b),.op(opA1),.y(outA1));
athena_alu32 ua2(.a(x2_a),.b(x2_b),.op(opA2),.y(outA2));
athena_alu32 ua3(.a(x3_a),.b(x3_b),.op(opA3),.y(outA3));
athena_alu32 ua4(.a(x4_a),.b(x4_b),.op(opA4),.y(outA4));
athena_alu32 ua5(.a(x5_a),.b(x5_b),.op(opA5),.y(outA5));
wire [31:0] raw0; athena_alu32 ub0(.a(ia0),.b(ib0),.op(opB0),.y(raw0)); assign outB0=enB0?raw0:32'b0;
wire [31:0] raw1; athena_alu32 ub1(.a(ia1),.b(ib1),.op(opB1),.y(raw1)); assign outB1=enB1?raw1:32'b0;
wire [31:0] raw2; athena_alu32 ub2(.a(ia2),.b(ib2),.op(opB2),.y(raw2)); assign outB2=enB2?raw2:32'b0;
wire [31:0] raw3; athena_alu32 ub3(.a(ia3),.b(ib3),.op(opB3),.y(raw3)); assign outB3=enB3?raw3:32'b0;
wire [31:0] raw4; athena_alu32 ub4(.a(ia4),.b(ib4),.op(opB4),.y(raw4)); assign outB4=enB4?raw4:32'b0;
wire [31:0] raw5; athena_alu32 ub5(.a(ia5),.b(ib5),.op(opB5),.y(raw5)); assign outB5=enB5?raw5:32'b0;
endmodule
