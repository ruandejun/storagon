FROM python:3.9.5

LABEL org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.name="storagon" \
      org.label-schema.description="Python ${PYTHON_VERSION}, PIP and other dependencies" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/storagon/" \
      org.label-schema.vendor="storagon" \
      org.label-schema.version=${VERSION} \
      org.label-schema.schema-version="1.0" \
      authors="Vincent Tran 'tranvietanh1991@gmail.com'"

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING UTF-8

#Python 2.17.13 already exist in Debian, so install only other dependencies.
RUN apt-get update -y --force-yes && apt-get install -y --force-yes --no-install-recommends \
    cron \
    gettext \
    python-setuptools \
    python-dev \
    rsyslog \
    logrotate \
    curl \
    postgresql-contrib \
    postgresql-client \
    postgresql \
    && apt-get upgrade -y --force-yes \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* /var/cache/apt/* /var/lib/apt/lists/*

RUN mkdir -p /opt/project/

WORKDIR /opt/project/

ADD ./pip_requirement.txt /opt/project/pip_requirement.txt
RUN pip3 install -r pip_requirement.txt

CMD ["python"]
