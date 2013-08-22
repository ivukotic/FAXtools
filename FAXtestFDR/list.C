int list(string fn){

TFile *f = TFile::Open(fn.c_str());
if (f) {
	f->ls();
	return 0;
	}
else 
	return -1;

}
