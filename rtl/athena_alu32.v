module athena_alu32(input [31:0] a,b, input [3:0] op, output reg [31:0] y);
always @* case(op)
0:y=a+b;1:y=a-b;2:y=a&b;3:y=a|b;4:y=a^b;
5:y=a<<b[4:0];6:y=a>>b[4:0];7:y=$signed(a)>>>b[4:0];
8:y={31'b0,($signed(a)<$signed(b))};9:y={31'b0,(a<b)};
10:y=~a;default:y=32'b0;
endcase
endmodule
