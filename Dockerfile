FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt requirements.txt

# add and run as non-root user
RUN adduser -D sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

RUN pip install --user -r requirements.txt
CMD ["python", "worker.py"]