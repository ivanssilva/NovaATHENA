module athena_pe_alu(
  input  [31:0] a, b,
  input  [3:0]  op,
  output [31:0] y
);
  athena_alu32 u(.a(a), .b(b), .op(op), .y(y));
endmodule

module athena_pe_c2(
  input  [31:0] a0, b0,
  input  [3:0]  op0,
  input  [31:0] b1,
  input  [3:0]  op1,
  input         bypass_b,
  output [31:0] y0,
  output [31:0] y1
);
  wire [31:0] chain;
  athena_alu32 ua(.a(a0), .b(b0), .op(op0), .y(chain));
  assign y0 = chain;
  // B consumes A as one operand. bypass_b exposes A directly when B is unused.
  wire [31:0] bout;
  athena_alu32 ub(.a(chain), .b(b1), .op(op1), .y(bout));
  assign y1 = bypass_b ? chain : bout;
endmodule
