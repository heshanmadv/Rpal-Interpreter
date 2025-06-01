**<h1>RPAL Interpreter</h1>**

This is the final group project done for the CS3513 - Programming Languages module in Semester 04.

<h2>Problem Description</h2>
It is required to implement a lexical analyzer and a parser for the RPAL language. Refer RPAL_Lex.pdf for the lexical rules and RPAL_Grammar.pdf for the grammar details.<br>Output of the parser should be the Abstract Syntax Tree (AST) for the given input program. Then need to implement an algorithm to convert the Abstract Syntax Tree (AST) in to Standardize Tree (ST) and implement CSE machine.<br>The program should be able to read an input file which contains a RPAL program.Output of your program should match the output of “rpal.exe“ for the relevant program.
<br>
<br>
<h3>Input and Output Requirements:</h3><br>
  Your program should execute using the following <br>
  <ul>
    <li>For Python:
      python .\myrpal.py file_name</li>
  </ul> 
Where file_name is the name of the file that has the RPAL program as the input.

Required switches:<br>
<ul>
  <li>-ast :  This switch prints the abstract syntax tree</li>
  <li>-st  :  This switch prints the standardized tree</li>
  <li>-l   :  This switch prints the input file content</li>
</ul>
