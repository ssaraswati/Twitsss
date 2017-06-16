FROM python:3

ADD * /

RUN apt-get update -yq
RUN apt-get upgrade -yq
#RUN apt-get install -yq

RUN pip install -r requirements.txt

CMD [ "python","-u", "./app.py" ]