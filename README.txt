Storage=Local
Working test files: #p4_1 #p4_2 #p4_3 #p4_4 #p4_5 #p4_6 #p4_7 #p4_8 #p4_9 #p4_10 #p4_11 #p4l1 

This program was written with Python. Python files do not require MAKEFILEs, so 
it would be pointless to make and/or require one.

I had to rename the parser file to "my_parser" to avoid shadowing an existing
python module.

The possible invocations are as follows:
  1. "comp"
      -if you want to write your file in the console

  2. "comp < file.cs4280"
      -if you want to redirect a file through stdin
      -"file" can be any name

  3. "comp file"
      -if you want to pass the file name as an argument
      -"file" can be any name