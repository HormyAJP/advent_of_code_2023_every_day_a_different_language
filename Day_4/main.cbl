IDENTIFICATION DIVISION.
PROGRAM-ID. AOC_DAY4.
*> Credit to the https://www.mainframestechhelp.com/tutorials/cobol
*> tutorial. Some of the comments describing various things are
*> copy-pasted from that tutorial.

ENVIRONMENT DIVISION.
INPUT-OUTPUT SECTION.
*> TODO: Understaind FILE-CONTROL better
FILE-CONTROL.
       SELECT TEST_INPUT_FILE ASSIGN TO "test_input.txt"
       ORGANIZATION IS LINE SEQUENTIAL.
       *> SELECT REAL_INPUT_FILE ASSIGN TO "real_input.txt"
       *> ORGANIZATION IS LINE SEQUENTIAL.

DATA DIVISION.
*> This section is used to describe the layout of files that are read
*> from or written to. FD is used for physical files. SD is used for
*> sort files
FILE SECTION.
FD TEST_INPUT_FILE.
*> FD REAL_INPUT_FILE.

*> HACKY: 100 is the max length of a line in the input file. I'm not
*> even going to attempt to make this dynamic at this stage.
*> TODO: Why is this in the FILE SECTION and not the WORKING-STORAGE?
*> NOTE: It seems common to prefix variables in working storage with WS.
01 WS-SCRATCH-CARD-LINE PIC X(100).

*> Defines variables and constants that are used throughout the program.
*> These are typically initialized each time the program starts
WORKING-STORAGE SECTION.
01  WS-END-OF-FILE PIC X(3) VALUE 'NO'.
01  WS-LINE-START PIC X(10).
01  WS-REST-OF-STRING PIC X(100).
01  WS-LINE-WINNING-NUMBERS PIC X(100).
01  WS-LINE-YOUR-NUMBERS PIC X(100).
01 WS-TRIMMED-LINE-WINNING-NUMBERS PIC X(100).


01  WS-CHAR-COUNT PIC 9(2) VALUE ZERO.
01  NDX PIC 9(3) VALUE ZERO. *> DELETE ME
01  NDX2 PIC 9(3) VALUE ZERO. *> DELETE ME
*> Input data has length 219 so assigning enough room for a 4 digit number.
01  WS-NUM-WINNING_NUMBERS PIC 9(4).
01  WS-TABLE-WINNING-NUMBERS.
    05  WINNING-NUMBER PIC 9(3) OCCURS 0 TO 1000 TIMES DEPENDING ON WS-NUM-WINNING_NUMBERS.

PROCEDURE DIVISION.
       OPEN INPUT TEST_INPUT_FILE.
       PERFORM UNTIL WS-END-OF-FILE = 'YES'
           READ TEST_INPUT_FILE
           AT END
               MOVE 'YES' TO WS-END-OF-FILE
           NOT AT END
               PERFORM PROCESS-LINE
           END-READ
       END-PERFORM.
       CLOSE TEST_INPUT_FILE.
       STOP RUN.

PROCESS-LINE.
      *>
       DISPLAY "Processing record: " WS-SCRATCH-CARD-LINE.

       *> First split the input string by colon and get rid of the
       *> "Card xxx:" part
       UNSTRING WS-SCRATCH-CARD-LINE DELIMITED BY ":"
           INTO WS-LINE-START WS-REST-OF-STRING
               ON OVERFLOW DISPLAY "Error when splitting input string by :"
       END-UNSTRING.

       *> Next split up the winning numbers and our numbers
       UNSTRING WS-REST-OF-STRING DELIMITED BY "|"
           INTO WS-LINE-WINNING-NUMBERS WS-LINE-YOUR-NUMBERS
               ON OVERFLOW DISPLAY "Error when splitting input string by |"
           NOT ON OVERFLOW
               DISPLAY "WS-LINE-WINNING-NUMBERS:  ", WS-LINE-WINNING-NUMBERS, " END"
               DISPLAY "WS-LINE-YOUR-NUMBERS:  ", WS-LINE-YOUR-NUMBERS
       END-UNSTRING.

       *> Strip leading and trailing whitespace
       *> Find the first non-whitespace
       PERFORM VARYING NDX FROM 1 by 1
           UNTIL WS-LINE-WINNING-NUMBERS (NDX:1) <> SPACE
           OR NDX = LENGTH OF WS-LINE-WINNING-NUMBERS
       END-PERFORM.

       *> Find the last non-whitespace
       PERFORM VARYING NDX2 FROM LENGTH OF WS-LINE-WINNING-NUMBERS by -1
           UNTIL WS-LINE-WINNING-NUMBERS(NDX2:1) <> SPACE
           OR NDX2 = NDX
       END-PERFORM.
       SUBTRACT NDX FROM NDX2.

       MOVE WS-LINE-WINNING-NUMBERS (NDX:NDX2) TO WS-TRIMMED-LINE-WINNING-NUMBERS.
       *> Count the number of numbers. We'll need this for array
       *> iteration.
       SET WS-CHAR-COUNT TO ZERO.
       INSPECT WS-TRIMMED-LINE-WINNING-NUMBERS TALLYING WS-CHAR-COUNT
           FOR ALL " ".

       ADD 1 TO WS-CHAR-COUNT

       DISPLAY "FOUND " WS-CHAR-COUNT " WINNING NUMBERS".


