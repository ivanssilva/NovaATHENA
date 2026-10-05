// Step 4C.3 canonical sparse-topology finalists.
// Structural physical-cost experiment only; MUL excluded (separate pipelined resource).
module athena_step4c3 #(parameter K=5)(
 input [31:0] x0,x1,x2,x3,x4,x5,x6,x7,
 input [3:0] op0,op1,op2,op3,op4,op5,op6,op7,
 output [31:0] y0,y1,y2,y3,y4,y5,y6,y7);
 wire [31:0] a0,a1,a2,a3,c0a,c0b,c1a,c1b;
 // K4 representative: A0->C0A, A1->C1B, C1A->A2, C1B->C0B.
 // K5 representative adds/rearranges to canonical Pareto class:
 // A0->A1, A1->C0B, A2->C1B, C1A->C0A, C1B->A3.
 // K6 representative: A0->A1, A2->C0A, A3->C1B, C0A->A1, C1A->A3, C1B->C0B.
 // Each selective destination receives a 2:1 source selector controlled by op MSB;
 // this intentionally exposes real mux+wire logic to synthesis while retaining ALU functionality.
 wire [31:0] iA1=(K==4)?x1:((K==5)?(op1[3]?a0:x1):(op1[3]?c0a:a0));
 wire [31:0] iA2=(K==4)?(op2[3]?c1a:x2):x2;
 wire [31:0] iA3=(K==6)?(op3[3]?c1a:x3):((K==5)?(op3[3]?c1b:x3):x3);
 wire [31:0] iC0A=(K==4)?(op4[3]?a0:x4):((K==5)?(op4[3]?c1a:x4):(op4[3]?a2:x4));
 wire [31:0] iC0B=(K==4)?(op5[3]?c1b:c0a):((K==5)?(op5[3]?a1:c0a):(op5[3]?c1b:c0a));
 wire [31:0] iC1B=(K==4)?(op7[3]?a1:c1a):((K==5)?(op7[3]?a2:c1a):(op7[3]?a3:c1a));
 athena_alu32 u0(.a(x0),.b(x1),.op(op0),.y(a0));
 athena_alu32 u1(.a(iA1),.b(x2),.op(op1),.y(a1));
 athena_alu32 u2(.a(iA2),.b(x3),.op(op2),.y(a2));
 athena_alu32 u3(.a(iA3),.b(x4),.op(op3),.y(a3));
 athena_alu32 u4(.a(iC0A),.b(x5),.op(op4),.y(c0a));
 athena_alu32 u5(.a(iC0B),.b(x6),.op(op5),.y(c0b));
 athena_alu32 u6(.a(x6),.b(x7),.op(op6),.y(c1a));
 athena_alu32 u7(.a(iC1B),.b(x0),.op(op7),.y(c1b));
 assign y0=a0;assign y1=a1;assign y2=a2;assign y3=a3;assign y4=c0a;assign y5=c0b;assign y6=c1a;assign y7=c1b;
endmodule
module athena_top_k4(input [31:0] x0,x1,x2,x3,x4,x5,x6,x7,input [3:0] op0,op1,op2,op3,op4,op5,op6,op7,output [31:0] y0,y1,y2,y3,y4,y5,y6,y7);
 athena_step4c3 #(.K(4)) u(.*); endmodule
module athena_top_k5(input [31:0] x0,x1,x2,x3,x4,x5,x6,x7,input [3:0] op0,op1,op2,op3,op4,op5,op6,op7,output [31:0] y0,y1,y2,y3,y4,y5,y6,y7);
 athena_step4c3 #(.K(5)) u(.*); endmodule
module athena_top_k6(input [31:0] x0,x1,x2,x3,x4,x5,x6,x7,input [3:0] op0,op1,op2,op3,op4,op5,op6,op7,output [31:0] y0,y1,y2,y3,y4,y5,y6,y7);
 athena_step4c3 #(.K(6)) u(.*); endmodule
