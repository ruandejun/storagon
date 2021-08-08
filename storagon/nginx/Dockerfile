FROM nginx:alpine
MAINTAINER V.Anh Tran "vincent.tran@grabtaxi.com"
RUN apk add --update curl && \
    rm -rf /var/cache/apk/*
RUN mkdir -p /var/www/storagon/media && \
    mkdir -p /var/www/storagon/static && \
    mkdir -p /var/www/conf/ && \
    mkdir -p /var/log/nginx/
WORKDIR /var/www/storagon
COPY storagon/nginx/nginx.conf /var/www/conf/nginx.conf
COPY storagon/nginx/htpasswd.txt /var/www/conf/htpasswd.txt
COPY storagon/nginx/mime.types /var/www/conf/mime.types
COPY storagon/nginx/uwsgi_params /var/www/conf/uwsgi_params
COPY static /var/www/storagon/static

EXPOSE 80 443
CMD ["nginx", "-c", "/var/www/conf/nginx.conf"]
