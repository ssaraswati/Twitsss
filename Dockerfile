FROM python:3.6-alpine
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD logstyles.py logstyles.py
ADD app.py app.py
CMD [ "python","-u", "./app.py" ]