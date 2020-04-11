FROM nvidia/cuda:10.2-cudnn7-runtime-ubuntu18.04

# Add this to the path for TensorFlow
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV ANACONDA_VERSION=2019.10
ENV CONDA_DIR=/opt/conda
RUN apt-get update --fix-missing && \
    apt-get install -y wget curl bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 git mercurial subversion && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# ENV ANACONDA_VERSION=2019.10
# RUN wget --quiet https://repo.anaconda.com/archive/Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh -O ~/anaconda.sh && \
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_DIR && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    find $CONDA_DIR -follow -type f -name '*.a' -delete && \
    find $CONDA_DIR -follow -type f -name '*.js.map' -delete && \
    $CONDA_DIR/bin/conda clean --all --yes --dry-run
RUN TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    rm -rf /var/lib/apt/lists/*
# "
RUN mkdir -p ~/.jupyter && { \
    echo "c.NotebookApp.allow_root = True"; \
    echo "c.NotebookApp.ip = '0.0.0.0'"; \
    echo "c.NotebookApp.token = ''"; \
    echo "c.JupyterLabTemplates.template_dirs = ['/root/template']"; \
    echo "c.JupyterLabTemplates.include_default = True"; \
    } | tee ~/.jupyter/jupyter_notebook_config.py
ENV PATH /opt/conda/bin:$PATH
RUN apt-get update --fix-missing && \
    apt-get install -y build-essential libxml2-dev fish fonts-ipafont fonts-ipaexfont fonts-noto-cjk libxml2 \
    #   autoconf automake libtool zlib1g-dev libicu-dev libpango1.0-dev libcairo2-dev \
    #   libgomp1 libgif7 libwebpmux3 libwebp6 libopenjp2-7 libpng16-16 libtiff5 zlib1g libopencv-dev libleptonica-dev swig && \
    #   tesseract-ocr libtesseract-dev tesseract-ocr-jpn tesseract-ocr-eng \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# SHELL ["/bin/bash", "-c"]
RUN $CONDA_DIR/bin/conda install jupyterlab psycopg2 ipywidgets nodejs jupyter && \
    $CONDA_DIR/bin/conda install -c conda-forge python-language-server texlive-core pandoc bash_kernel awscli && \
    pip install jupyterlab_sql jupyterlab-git jupyter_bokeh jupyterlab_latex jupyterlab_templates jupyter_bokeh nbdime && \
    pip install flake8 flake8-SQL flake8-bandit flake8-broken-line flake8-bugbear flake8-builtins flake8-import-order flake8-spellcheck flake8-strict flake8-string-format pandas-vet pep8-naming jupyter-lsp && \
    jupyter labextension install @jupyterlab/plotly-extension --no-build && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter labextension install @bokeh/jupyter_bokeh --no-build && \
    # jupyter labextension install jupyterlab-flake8 --no-build && \
    # jupyter labextension install @ryantam626/jupyterlab_code_formatter --no-build && \
    # Code Formatter https://github.com/ryantam626/jupyterlab_code_formatter
    # conda install -c jupyterlab_code_formatter && \
    # https://github.com/mlshapiro/jupyterlab-flake8
    # https://github.com/krassowski/jupyterlab-lsp
    jupyter labextension install @krassowski/jupyterlab-lsp --no-build && \
    # jupyter serverextension enable --py jupyterlab_code_formatter && \
    # Git-Sidebar https://github.com/jupyterlab/jupyterlab-git
    # Latex https://github.com/jupyterlab/jupyterlab-latex
    jupyter labextension install @jupyterlab/latex --no-build && \
    jupyter serverextension enable --sys-prefix jupyterlab_latex && \
    # Contents Table https://github.com/jupyterlab/jupyterlab-toc
    jupyter labextension install @jupyterlab/toc --no-build && \
    # Template Reader https://github.com/jpinzonc/jupyterlab_templates
    jupyter labextension install jupyterlab_templates --no-build && \
    jupyter serverextension enable --py jupyterlab_templates && \
    # Diff tool https://nbdime.readthedocs.io/en/latest/extensions.html
    jupyter labextension install nbdime-jupyterlab --no-build && \
    # Spellchecker
    # https://github.com/ijmbarr/jupyterlab_spellchecker
    # jupyter labextension install @ijmbarr/jupyterlab_spellchecker && \
    jupyter serverextension enable jupyterlab_sql --py --sys-prefix && \
    # widgetnbextension  https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
    # jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    # jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    # jupyter lab build --dev-build=False && \
    jupyter lab build && \
        jupyter lab clean && \
        npm cache clean --force && \
        rm -rf $HOME/.node-gyp && \
        rm -rf $HOME/.local && \
        find /opt/conda/ -follow -type f -name '*.a' -delete && \
        find /opt/conda/ -follow -type f -name '*.js.map' -delete
COPY ./environment.yaml /tmp
RUN $CONDA_DIR/bin/conda config --system --prepend channels conda-forge && \
    $CONDA_DIR/bin/conda env update -f /tmp/environment.yaml && \
    echo "conda activate $(head -1 /tmp/environment.yaml | cut -d' ' -f2)" >> ~/.bashrc && \
    $CONDA_DIR/bin/conda run -n  $(head -1 /tmp/environment.yaml | cut -d' ' -f2) ipython kernel install --user --name=$(head -1 /tmp/environment.yaml | cut -d' ' -f2) && \
    rm /tmp/environment.yaml && \
    $CONDA_DIR/bin/conda clean --all --yes --dry-run
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yaml | cut -d' ' -f2)/bin:$PATH
EXPOSE 8888
ENTRYPOINT [ "/usr/bin/tini", "--" ]
# CMD [ "/bin/bash" ]
