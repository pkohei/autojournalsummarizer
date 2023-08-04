FROM python:3.10

RUN apt-get update \
    && apt-get -y install locales libsndfile1 \
    && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8 LANGUAGE=ja_JP:ja LC_ALL=ja_JP.UTF-8 TZ=JST-9
ENV DEBUG_MODE=1

# ユーザー追加
ARG UID=1000
ARG GID=1000
ARG USERNAME=app
ARG GROUPNAME=app
RUN groupadd -g ${GID} ${GROUPNAME} && \
    useradd -m -s /bin/bash -u ${UID} -g ${GID} ${USERNAME}
USER ${USERNAME}

COPY Pipfile Pipfile.lock /home/${USERNAME}/code/

RUN pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy && \
    pip uninstall -y pipenv virtualenv-clone virtualenv
