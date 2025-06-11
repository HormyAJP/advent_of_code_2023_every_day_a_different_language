#!/usr/bin/env perl

use strict; # Ensure variables are defined and other nice things
use warnings; # Better diagnostics

sub assert_equal {
    my ($actual, $expected) = @_;
    if ($actual != $expected) {
       die "Assertion failed: $actual != $expected";
    }
}

sub dump_array {
    #
    # Print a 1 or 2-D array to stdout
    #
    my @array = @_;
    foreach my $var (@array) {
        if (ref($var) eq 'ARRAY') {
            print(join('', @$var), "\n");
        }
    }
}

sub parse_input {
    # The below can be done with the following one liner:
    # my @lines = map { [ split '', $_ ] } map { chomp; $_ } <HANDLE>;
    # However, I wanted to break things up to understand them better.

    my ($filename) = @_;
    open(HANDLE, '<', $filename) or die "Could not open file: $!";
    my @lines = <HANDLE>;
    close HANDLE;

    # Remove new lines. Note that this mutates @lines
    map { chomp; $_ } @lines;

    # These two lines are equivalent. The square bracket notation is a more concise way to return
    # a reference to the returned array.
    # @lines = map { my @sp = split('', $_); \@sp } @lines;
    # Split lines into arrays
    @lines = map { [ split('', $_) ] } @lines;
    return \@lines;
}

sub transpose {
    my ($matrix) = @_;
    my @tr;
    my $row_length = @$matrix;
    for my $irow (0..$row_length-1) {
        my $col_length = @{@$matrix[$irow]};
        for my $col (0..$col_length-1) {
            $tr[$col][$irow] = @{@$matrix[$irow]}[$col];
        }
    }
    return \@tr;
}

sub expand_universe {
    my ($universe_ref) = @_;
    my @new_rows;
    # We have to dereference universe_ref first. But then each $row will be a reference to another
    # array
    foreach my $row (@$universe_ref) {
        push @new_rows, $row;
        # TODO: ???
        push @new_rows, $row if scalar(grep { $_ eq '.' } @$row) == scalar(@$row);
    }

    # my @transposed = map { [ map { $_->[$_] } @new_rows ] } 0..$#{$new_rows[0]};
    my $transposed = transpose(\@new_rows);
    my @new_cols;
    foreach my $col (@$transposed) {
        push @new_cols, $col;
        push @new_cols, $col if scalar(grep { $_ eq '.' } @$col) == scalar(@$col);
    }

    # my @result = map { [ map { $_->[$_] } @new_cols ] } 0..$#new_cols;
    return transpose(\@new_cols);
}

sub distance_between_galaxies {
    my ($index1, $index2) = @_;
    return abs($index2->[1] - $index1->[1]) + abs($index2->[0] - $index1->[0]);
}

sub coordinates_of_galaxies {
    my ($universe) = @_;
    my @coords;
    for my $irow (0 .. $#$universe) {
        for my $icol (0 .. $#{$universe->[$irow]}) {
            push @coords, [$irow, $icol] if $universe->[$irow][$icol] eq '#';
        }
    }
    return \@coords;
}

sub answer_part1 {
    my ($filename) = @_;
    # Universe will be a reference to an array of array references (vomit)
    my $universe = parse_input($filename);
    $universe = expand_universe($universe);
    my $coords = coordinates_of_galaxies($universe);
    my $sum_distances = 0;
    for my $icoord (0 .. $#$coords) {
        for my $j ($icoord + 1 .. $#$coords) {
            $sum_distances += distance_between_galaxies($coords->[$icoord], $coords->[$j]);
        }
    }
    return $sum_distances;
}

assert_equal(answer_part1('test_input.txt'), 374);
assert_equal(answer_part1('real_input.txt'), 9556896);

# N.B. I didn't convert part 2 to Perl. I'd had enough by this point!
