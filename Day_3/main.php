#!/usr/bin/env php
<?php

function debugDumpMatrix($matrix) {
   foreach ($matrix as $row) {
      foreach ($row as $col) {
         echo $col;
      }
      echo "\n";
   }
}

function debugDumpAsterisksToNumbersMap($asterisksToNumbersMap) {
   foreach ($asterisksToNumbersMap as $index => $numbers)
   {
      echo $index . " => ";
      foreach ($numbers as $number) {
         echo $number . " ";
      }
      echo "\n";
   }
}

function unpackLinesToMatrix($lines) {
   $rows = count($lines);
   $cols = strlen($lines[0]);

   $matrix = array();
   // We pad our matrix with an extra row and column on each side to make
   // the subseuqent logic of checking if a number is a "part number" easier.
   for ($i = 0; $i < $rows + 2; $i++) {
      $matrix[$i] = array_fill(0, $cols + 2, '0');
   }

   $outputLine = 0;
   foreach ($lines as $line) {
      $outputLine++;
      $outoutColumn=0;
      if (strlen($line) != $cols) {
         // We make an assumption that the input line lengths are the same.
         throw("Input line length is not consistent\n");
      }
      foreach (str_split($line) as $char) {
         $outoutColumn++;
         $matrix[$outputLine][$outoutColumn] = $char;
      }
   }
   return $matrix;
}

function readInputDataToMatrix($filename) {
   $f = fopen($filename, "r") or die("Unable to open file!");
   if ($f) {
      $lines = explode("\n", fread($f, filesize($filename)));
   } else {
      throw("Unable to open inputfile $filename!\n");
   }
   fclose($f);
   return unpackLinesToMatrix($lines);
}

function surroundingIndices($matrix, $row, $col) {
   return array(
      [$row-1, $col-1],
      [$row-1, $col],
      [$row-1, $col+1],
      [$row, $col-1],
      [$row, $col+1],
      [$row+1, $col-1],
      [$row+1, $col],
      [$row+1, $col+1]
   );
}

function surroundingSquaresHaveSymbol($matrix, $row, $col) {
   $surroundingIndices = surroundingIndices($matrix, $row, $col);

   foreach ($surroundingIndices as $index) {
      $value= $matrix[$index[0]][$index[1]];
      if (is_numeric($value) || $value == '.') {
         continue;
      } else {
         return true;
      }
   }
   return false;
}

function determinPartNumbers($matrix) {
   $partNumbers = array();

   // Note that we start iteration at row/col 1 and skip the final row/col. This
   // is because we padded our data with a border of zeros.
   for ($irow = 1; $irow < count($matrix) - 1; $irow++) {
      $isPartNumber = false;
      $currentNumber = "";

      for ($icol = 1; $icol < count($matrix[0]) - 1; $icol++) {
         $thisCharacter = $matrix[$irow][$icol];

         if (is_numeric($thisCharacter)) {
            $currentNumber .= $thisCharacter;
            // No point calling surroundingSquaresHaveSymbol if we already
            // know this is a part number
            if ($isPartNumber == false && surroundingSquaresHaveSymbol($matrix, $irow, $icol)) {
               $isPartNumber = true;
            }
         } else {
            if ($isPartNumber) {
               array_push($partNumbers, intval($currentNumber));
            }
            $isPartNumber =  false;
            $currentNumber = "";
         }
      }
      // Handle the case where we reach the each of the row and the last digit of the number
      // was at the end of the row.
      if ($currentNumber != "" && $isPartNumber == true) {
         array_push($partNumbers, intval($currentNumber));
      }
   }
   return $partNumbers;
}

function computePart1($filename) {
   $matrix = readInputDataToMatrix($filename);
   $partNumbers = determinPartNumbers($matrix);
   return array_sum($partNumbers);
}

try {
   assert(computePart1("test_input_part1.txt") == 4361);
   print("Answer to Part 1 is " . computePart1("real_input.txt") . "\n");
} catch (Exception $e) {
   echo 'Caught exception: ',  $e->getMessage(), "\n";
   exit(1);
}

function coordiatesOfAdjacentAsterisks($matrix, $row, $col) {
   $surroundingCogIndices = array();
   $surroundingIndices = surroundingIndices($matrix, $row, $col);
   foreach ($surroundingIndices as $index) {
      $value= $matrix[$index[0]][$index[1]];
      if ($value != '*') {
         continue;
      }
      array_push($surroundingCogIndices, $index);
   }
   return $surroundingCogIndices;
}

function indexToString($index) {
   return $index[0] . "," . $index[1];
}

function determinGearNumbers($matrix) {
   $gearNumbers = array();
   $asterisksToNumbersMap = array();
   // Note that we start iteration at row/col 1 and skip the final row/col. This
   // is because we padded our data with a border of zeros.
   for ($irow = 1; $irow < count($matrix) - 1; $irow++) {
      $currentNumber = "";
      $indicesOfTouchingAsterisks = array();

      for ($icol = 1; $icol < count($matrix[0]) - 1; $icol++) {
         $thisCharacter = $matrix[$irow][$icol];

         if (is_numeric($thisCharacter)) {
            $currentNumber .= $thisCharacter;
            $indicesOfTouchingAsterisks += coordiatesOfAdjacentAsterisks($matrix, $irow, $icol);
         } else {
            foreach ($indicesOfTouchingAsterisks as $index) {
               $key = indexToString($index);
               if (!array_key_exists($key, $asterisksToNumbersMap)) {
                  $asterisksToNumbersMap[$key] = array();
               }
               array_push($asterisksToNumbersMap[$key], intval($currentNumber));
            }
            $currentNumber = "";
            $indicesOfTouchingAsterisks = array();
         }
      }
      // Handle the case where we reach the each of the row and the last digit of the number
      // was at the end of the row.
      if ($currentNumber != "") {
         // Yuck. Copy paste from above. Should be a function.
         foreach ($indicesOfTouchingAsterisks as $index) {
            $key = indexToString($index);
            if (!array_key_exists($key, $asterisksToNumbersMap)) {
               $asterisksToNumbersMap[$key] = array();
            }
            array_push($asterisksToNumbersMap[$key], intval($currentNumber));
         }
      }
   }

   // Should have broken this out into another function
   foreach ($asterisksToNumbersMap as $index => $numbers)
   {
      $numbers = array_unique($numbers);
      if (count($numbers) == 2) {
         array_push($gearNumbers, $numbers[0] * $numbers[1]);
      }
   }
   return $gearNumbers;
}

function computePart2($filename) {
   $matrix = readInputDataToMatrix($filename);
   $gearNumbers = determinGearNumbers($matrix);
   return array_sum($gearNumbers);
}

try {
   assert(computePart2("test_input_part1.txt") == 467835);
   print("Answer to Part 2 is " . computePart2("real_input.txt"));
} catch (Exception $e) {
   echo 'Caught exception: ',  $e->getMessage(), "\n";
   exit(1);
}

?>
