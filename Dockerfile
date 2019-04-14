FROM python:3-alpine

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check --quiet --requirement /tmp/requirements.txt

COPY roster.py /usr/bin/roster

USER nobody

CMD [ "/usr/bin/roster" ]
