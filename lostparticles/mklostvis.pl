#!/usr/bin/perl
#
# This perl script reads MCNP/MCNPX output files to find lost particle information
#           and then writes a cubit journal file to stdout to visualize the lost 
#           particles using two vertices and a curve connecting them.  The curve 
#           length must be set by the user on the command line.
# to use:
#         mklostvis.pl mcnpoutputfilename curvelength
#  e.g.   mklostvis.pl hpl4bo 10
#         mklostvis.pl hpl4bo 10 >cubithpl4b.jou (redirects stdout to a file)
#
# notes:
#   -currently writes to stdout
#   -prints messages prepended with # so cubit treats them as a comment
#   -embeds some cubit commands for convenience
#   -fixes problem if the number of lost particles is greater than 999 due to format statement in mcnp and uses counter for ilost since mcnp reports multiples in parallel runs
#   -fixed problem if the number of lost particles is greater than 99 due to lack of a space separator (5/23/2012)
#      e.g.
#1   lost particle no.349     no intersection found in subroutine track     history no.    98585339
#
# turn off strict and warnings to sidestep problem comparing against blank lines
#use strict;
#use warnings; 
#
#
# get filename from argument list
my $filename=$ARGV[0];
# open filename
open FILEIN, $filename or die "Cannot open $filename for read:$!";
# 
# get number of lost particles in file (and die if there are none)
print "\#...checking for lost particles in: $filename--";
my $nlostparticles=`grep ^'1   lost particle no' $filename | wc -l`;
chomp $nlostparticles;
print "there are $nlostparticles lost particles\n";
if($nlostparticles==0){
    die "Sorry, there are $nlostparticles lost particles!\n";
}
#
# get length of curves for visualization from argument list
my $curvelength=$ARGV[1];
print "\#   will use a curve length of: $curvelength\n";
if($curvelength<=0){
    die "Sorry, bad curve length: $curvelength\n";
}
#
print "\#Everything looks OK, will process the file now...\n";
#
# set counter for current number of lost particles
$ilost=0;
# keep reading lines in the file until we reach a lost particle, then process it
while (<FILEIN>){
    my @line=split;
#    print "@line\n"; # prints the whole line
#   check if line is a lost particle line and print lost particle number and nps
    if($line[0] eq "1" and $line[1] eq "lost" and $line[2] eq "particle"){
#       add a space after each string "no." to make sure this is processed correctly
        my $wholetempline=join " ",@line; # create a temp line with elements separated by space
        $wholetempline=~ s/\./. /g; # replace a period with period space
        #print "wholetempline is $wholetempline\n"; # prints the whole temp line
	my @templine=split /\s+/,$wholetempline;
	$ilost=$ilost+1;
	$inps=$templine[13];
#	print " templost $templine[4] $templine[13] \n"; # prints lost particle number and nps
    }elsif($line[0] eq "x,y,z" and $line[1] eq "coordinates:"){
        $x=$line[2];
        $y=$line[3];
        $z=$line[4];
	#print " $line[2] $line[3] $line[4]"; # prints x,y,z
    }elsif($line[0] eq "u,v,w" and $line[1] eq "direction" and $line[2] eq "cosines:"){
        $u=$line[3];
        $v=$line[4];
        $w=$line[5];     
	#print " $line[3] $line[4] $line[5]"; # prints u,v,w
    }elsif($line[0] eq "energy" and $line[1] eq "=" and $line[3] eq "weight" and $line[4] eq "="){
        $erg=$line[2];
	$wgt=$line[5];
        $tme=$line[8];
	#print " $line[2] $line[5] $line[8]\n"; # prints erg,wgt,time
        # at this point in the if/elsifs I have all the phase space information
        #                                 for the lost particle
        #print "$ilost $inps $x $y $z $u $v $w $erg $wgt $tme\n"; # print all info
        print "create vertex $x $y $z color red\n";
        print "vertex {Id(\"vertex\")} name \"v1nps${inps}_ilost${ilost}\"\n";# name the vertex v1$inps_$ilost
        # now calculate the second vertex assuming some curvelength 
	$xnew=$x+$u*$curvelength;
	$ynew=$y+$v*$curvelength;
	$znew=$z+$w*$curvelength;
        print "create vertex $xnew $ynew $znew color green\n";
        print "vertex {Id(\"vertex\")} name \"v2nps${inps}_ilost${ilost}\"\n";# name the vertex v2$inps_$ilost
        # next create curve joining the two vertices
        print "create curve vertex v1nps${inps}_ilost${ilost} v2nps${inps}_ilost${ilost}\n";
        print "curve {Id(\"curve\")} name \"losttracknps${inps}_ilost${ilost}\"\n";# name the curve losttrack$inps_$ilost
        print "group \"nps${inps}\" add vertex v1nps${inps}_ilost${ilost} v2nps${inps}_ilost${ilost}, curve {Id(\"curve\")} \n"; # add vertices,curve to group nps${inps}
    } # close elsif for energy,wgt,time 
} # close while filein loop
#
# add line to turn on named curves in cubit file
print "\# turn on named curve labels\n"; # comment line for cubit file
print "label curve name only\n";
#
print "\#\n";
print "\# Example cubit commands that may be useful: \n"; # comment line for cubit file
print "\# label off\n"; # comment line for cubit file
print "\# draw vertex with name 'v1*' curve with name 'losttrack*' volume 12 \n"; # comment line for cubit file
#
print "\#All done!\n";
close FILEIN;
