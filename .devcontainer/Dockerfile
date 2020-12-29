FROM python:3.9-buster

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" && echo $SNIPPET >> "/root/.bashrc"

RUN apt-get update -y && apt-get install \
    # For numpy
    libblas-dev liblapack-dev \
    # Scipy
    gfortran -y

# For Jupyter
RUN mkdir -p /root/.jupyter/
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

ENV POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python
ENV PATH /root/.poetry/bin:${PATH}

COPY poetry.* ./
COPY pyproject.toml .
RUN poetry install

# TODO: figure out the poetry add syntax
RUN pip install "git+https://github.com/NathanDeMaria/EndGame#egg=endgame-matcher&subdirectory=matcher"
RUN pip install "git+https://github.com/NathanDeMaria/EndGame#egg=py-endgame&subdirectory=py-endgame"

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--NotebookApp.token=''", "--NotebookApp.password=''", "--allow-root"]
