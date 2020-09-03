#include <vector>
#include <list>
#include <queue>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <cstdio>


using namespace std;

int main(int argc, char* argv[]) {

    if(argc != 2) {
      cerr << "Usage error: expected <executable> <input>" << endl;
      exit(1);
    }

    ifstream ifs(argv[1]);
    if(!ifs) {
      cerr << "Input file not found." << endl;
      exit(1);
    }
    
    return 0;
}