FROM registry.docker-cn.com/library/python:3.6

RUN echo 'Asia/Shanghai' >/etc/timezone & cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ADD ./requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir

ADD . /mano
WORKDIR /mano
ENV LC_ALL="C.UTF-8" LANG="C.UTF-8" PYTHONPATH=/mano    


