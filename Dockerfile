FROM python:3.9-bookworm

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

# Install dependencies.
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    cron \
    gettext \
    rsyslog \
    logrotate \
    curl \
    postgresql-contrib \
    postgresql-client \
    postgresql \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* /var/cache/apt/* /var/lib/apt/lists/*

RUN mkdir -p /var/www/storagon
RUN mkdir -p /var/www/storagon/log

WORKDIR /var/www/storagon

ADD ./pip_requirement.txt /var/www/storagon/pip_requirement.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r pip_requirement.txt

RUN mkdir -p /var/log/uwsgi/

EXPOSE 8000 8889

CMD [ "sh", "-c", "uwsgi --ini storagon/uwsgi_config.ini"]
