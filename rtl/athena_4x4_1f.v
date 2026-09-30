module athena_4x4_1f(
input [31:0] x0_a,x0_b, input [3:0] opA0, output [31:0] outA0,
input [31:0] x1_a,x1_b, input [3:0] opA1, output [31:0] outA1,
input [31:0] x2_a,x2_b, input [3:0] opA2, output [31:0] outA2,
input [31:0] x3_a,x3_b, input [3:0] opA3, output [31:0] outA3,
input [31:0] b0_a,b0_b, input [3:0] opB0, input enB0, output [31:0] outB0,
input [1:0] sel0, input use_fwd0,
input [1:0] sel_fuse, input use_fuse,
input [31:0] b1_a,b1_b, input [3:0] opB1, input enB1, output [31:0] outB1,
input [1:0] sel1, input use_fwd1,
input [31:0] b2_a,b2_b, input [3:0] opB2, input enB2, output [31:0] outB2,
input [1:0] sel2, input use_fwd2,
input [31:0] b3_a,b3_b, input [3:0] opB3, input enB3, output [31:0] outB3,
input [1:0] sel3, input use_fwd3
);
wire [31:0] fwd0 = sel0==0 ? outA0 : sel0==1 ? outA1 : sel0==2 ? outA2 : outA3;
wire [31:0] ia0=use_fwd0?fwd0:b0_a;
wire [31:0] ib0=use_fuse?(sel_fuse==0 ? outA0 : sel_fuse==1 ? outA1 : sel_fuse==2 ? outA2 : outA3):b0_b;
wire [31:0] fwd1 = sel1==0 ? outA0 : sel1==1 ? outA1 : sel1==2 ? outA2 : outA3;
wire [31:0] ia1=use_fwd1?fwd1:b1_a;
wire [31:0] ib1=b1_b;
wire [31:0] fwd2 = sel2==0 ? outA0 : sel2==1 ? outA1 : sel2==2 ? outA2 : outA3;
wire [31:0] ia2=use_fwd2?fwd2:b2_a;
wire [31:0] ib2=b2_b;
wire [31:0] fwd3 = sel3==0 ? outA0 : sel3==1 ? outA1 : sel3==2 ? outA2 : outA3;
wire [31:0] ia3=use_fwd3?fwd3:b3_a;
wire [31:0] ib3=b3_b;
athena_alu32 ua0(.a(x0_a),.b(x0_b),.op(opA0),.y(outA0));
athena_alu32 ua1(.a(x1_a),.b(x1_b),.op(opA1),.y(outA1));
athena_alu32 ua2(.a(x2_a),.b(x2_b),.op(opA2),.y(outA2));
athena_alu32 ua3(.a(x3_a),.b(x3_b),.op(opA3),.y(outA3));
wire [31:0] raw0; athena_alu32 ub0(.a(ia0),.b(ib0),.op(opB0),.y(raw0)); assign outB0=enB0?raw0:32'b0;
wire [31:0] raw1; athena_alu32 ub1(.a(ia1),.b(ib1),.op(opB1),.y(raw1)); assign outB1=enB1?raw1:32'b0;
wire [31:0] raw2; athena_alu32 ub2(.a(ia2),.b(ib2),.op(opB2),.y(raw2)); assign outB2=enB2?raw2:32'b0;
wire [31:0] raw3; athena_alu32 ub3(.a(ia3),.b(ib3),.op(opB3),.y(raw3)); assign outB3=enB3?raw3:32'b0;
endmodule
