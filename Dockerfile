FROM python:3.11-slim
ADD . /project
RUN pip3 install -r /project/requirements.txt
RUN apt-get update && apt-get install libgl1 -y
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6



ENTRYPOINT ["python", "/project/app.py"]

#FROM python:3.8-slim
#RUN useradd --create-home --shell /bin/bash app_user
#WORKDIR /home/app_user
#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt
#USER app_user
#COPY . .
#CMD ["bash"]