# https://dev.to/0xnari/deploying-fastapi-app-with-google-cloud-run-13f3
FROM python:3.11.3
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY . $APP_HOME/app
WORKDIR $APP_HOME/app

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]