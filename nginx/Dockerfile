FROM nginx:1.27-alpine

COPY nginx.conf.template /tmp/nginx.conf.template
COPY nginx-ssl.conf.template /tmp/nginx-ssl.conf.template
COPY docker-entrypoint.sh /docker-entrypoint-nginx.sh
RUN chmod +x /docker-entrypoint-nginx.sh

ENTRYPOINT ["/docker-entrypoint-nginx.sh"]
CMD ["nginx", "-g", "daemon off;"]
