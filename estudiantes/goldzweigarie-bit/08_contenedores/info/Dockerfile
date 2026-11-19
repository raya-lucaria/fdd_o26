FROM ubuntu:24.04
WORKDIR /app
COPY info.sh .
RUN chmod +x info.sh && date -u '+%Y-%m-%d %H:%M:%S UTC' > /app/fecha_build
CMD ["./info.sh"]
