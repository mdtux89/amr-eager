wget http://kinloch.inf.ed.ac.uk/public/direct/amreager/resources_single.tar.gz
tar -xf resources_single.tar.gz
rm -f resources_single.tar.gz

wget http://kinloch.inf.ed.ac.uk/public/direct/amreager/LDC2015E86.tar.gz # the model trained on LDC2015E86
tar -xf LDC2015E86.tar.gz
rm -f LDC2015E86.tar.gz

wget https://github.com/redpony/cdec/archive/master.zip
unzip master.zip
rm -f master.zip

wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip
unzip stanford-corenlp-full-2015-12-09.zip
rm -f stanford-corenlp-full-2015-12-09.zip
