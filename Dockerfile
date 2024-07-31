FROM python:3.10

RUN apt-get update && apt-get upgrade -y
RUN dpkg --configure -a
RUN apt-get --fix-broken install
RUN apt-get install -y \
	apt-utils \
	libgirepository1.0-dev \
	gstreamer-1.0 \
	gstreamer1.0-plugins-ugly \
	gstreamer1.0-plugins-good \
	gstreamer1.0-plugins-bad \
	gir1.2-gstreamer-1.0 \
	gir1.2-gst-plugins-base-1.0 \
	python3-gst-1.0 \
	gstreamer1.0-tools \
	gir1.2-ges-1.0 \
	gstreamer1.0-libav \
	ffmpeg

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -pv ~/.cache/xdgr
RUN export XDG_RUNTIME_DIR=$PATH:~/.cache/xdgr
RUN mkdir /xdg
ENV XDG_RUNTIME_DIR="/xdg"
ENV SSL_DISABLE=True
ENV GST_DEBUG="3,queue_dataflow:2"
WORKDIR /app

ENV PYTHONUNBUFFERED=0

COPY . .
RUN pip install -e src

CMD [ "python" , "/app/run.py" ]