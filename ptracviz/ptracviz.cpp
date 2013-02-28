#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
using namespace std;

// ptracviz.cpp (v1.1)
//
// This is a tool designed to parse a ptrac file from MCNP and
// convert it to a journal file in CUBIT for visualization.
//
// v1.0 -- Initial release
// v1.1 -- Improvements in logic, fixed some a bug so that
//         now individual event points can be displayed
//
// Known issues:
//
// Coloring of tracks and vertices is done by particle type
// unfortunately, it appears the location of this info moves
// depending on the data requested.  Need improvement in logic
// to address this.
//
// Usage:
//
// ./a.out [ptrac file] [journal file]
//
// defaults are "ptrac" and "ptr.jou" respectively
//

int main(int argc, char **argv) {

  int getptcl(string line, int ploc);
  int gettrkid(string line);
  int isbnk(string line);
  string getcolr(int ptl);

  int trkid = 1;
  const char *ptrac = "ptrac";
  const char *jou = "ptr.jou";
  
  if (argc >= 2) {
    ptrac = argv[1];
  }
  if (argc >= 3) {
    jou = argv[2];
  }
  
  string line;
  ifstream pfile (ptrac);
  ofstream jfile (jou);

// Open ptrac file and read until end  
  
  while (! pfile.eof() ) {
    getline(pfile,line);
// Check to see if we have reached a history header
    int headloc = line.find(" 1000");
    if (headloc == 16) {
      int flg = 0;
      int evnt = 0;
      int ploc = 35;  // String location to determine particle index
      string currloc;
      string prevloc;
// Assign track id
      trkid = gettrkid(line);
// Header found, loop until ptrac flag '9000' found and then stop
      while (flg == 0) {
        getline(pfile,line);
        int loc = line.find(" 9000");
        if (loc == 6) flg = 1;

// Determine if start of secondary radiation track
	int bnk = 0;
	if (flg == 0)
          bnk = isbnk(line);


// Parse the particle type
// First entry (ploc) in list had different order than subsequent ones
// so set ploc after initial header
	int ptl = getptcl(line,ploc);
	ploc = 45;

// Get the appropriate color
        string colr = getcolr(ptl);
	
        getline(pfile,line);
	currloc = line;

//        cout << "flg: " << flg << endl;
	
        if ((bnk == 0) && (flg == 0)&&(prevloc != currloc)) {
	  jfile << "create vertex " << currloc << " color " << colr << endl;
	  jfile << "group " << char(34) << "track_" << trkid << char(34)
		  << " add vertex {Id(" << char(34) << "vertex" << char(34)
		  << ")}" << endl;
	  if (evnt == 0)
	    jfile << "group " << char(34) << "src_pt" << char(34)
		    << " add vertex {Id(" << char(34) << "vertex" << char(34)
		    << ")}" << endl;
	}
// Displaying individual points is special
	else if ((evnt == 0) && (flg == 1)) {
          jfile << "create vertex " << currloc << " color " << colr << endl;
          jfile << "group " << char(34) << "src_pt" << char(34)
		  << " add vertex {Id(" << char(34) << "vertex" << char(34)
		  << ")}" << endl;
	}
	else {
          currloc.clear();
	  prevloc.clear();
	}
	
	evnt++;
	
// Draw path between previous point and current point
        if ((! prevloc.empty() ) && (prevloc != currloc)) {
          jfile << "create curve from location " << prevloc << " location "
		  << currloc << endl;
// Set curve to correct color
          jfile << "color curve " << "{Id(" << char(34) << "curve" 
	          << char(34) << ")} " << colr << endl;
          jfile << "group " << char(34) << "track_" << trkid << char(34)
                  << " add curve {Id(" << char(34) << "curve" << char(34)
                  << ")}" << endl; 
	}
	
	prevloc = currloc;
      }
    }
  }

  pfile.close();
  jfile.close();

  return 0;
}


// Function to extract particle index
int getptcl(string line, int ploc) {
  string ptlstr = line.erase(0,ploc);
  ptlstr.erase(6);

  const char* ptlcst = ptlstr.c_str(); 
  
  int ptlid = atoi(ptlcst);

  return ptlid;

}


// Function to extract track id
int gettrkid(string line) {
  string trkstr = line.erase(12);

  const char* trkcst = trkstr.c_str();

  return atoi(trkcst);

}



// Function to get the desired color
// n = red
// p = blue
// e = yellow
string getcolr(int ptl) {

  string colr;
  if (ptl == 1)
    colr = "red";
  if (ptl == 2)
    colr = "blue";
  if (ptl == 3)
    colr = "yellow";

  return colr;

}


// Function to determine if a banked event is beginning
int isbnk(string idstr) {

  idstr.erase(0,7);
  idstr.erase(1);
  const char* idcst = idstr.c_str();
  int id = atoi(idcst);

  if (id == 2)
    return 1;
  else
    return 0;
  
}
