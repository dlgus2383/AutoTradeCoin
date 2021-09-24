From ubuntu:18.04

RUN apt-get update -y  
RUN apt-get install -y python3
RUN apt-get install -y python3-pip 
Run apt-get install -y python3-dev

RUN pip3 install -r requirements.txt

RUN mkdir -p /main

COPY . /main

WORKDIR /main

ENTRYPOINT [ "python3" ]

CMD [ "main.py" ]