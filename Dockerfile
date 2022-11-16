FROM r-base

# Install base utilities
RUN apt-get update && \
    apt-get install -y build-essential  && \
    apt-get install -y wget && \
    apt-get install -y tabix && \
    apt-get install -y libreadline-dev && \
    apt-get clean && \
    apt-get install -y procps g++ && \
    rm -rf /var/lib/apt/lists/* 


# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh  -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN apt-get update && apt install -y procps g++ && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir software
COPY docker_resources/annovar /software/annovar
COPY . /software/renovo

RUN python -m pip install scikit-learn==0.20.3
RUN conda install -c r r-curl r-httr r-rvest r-readxl r-tidyverse
RUN conda install -c bioconda r-openxlsx
RUN pip install pandas matplotlib seaborn argparse
