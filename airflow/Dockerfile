# 1. a small Python image
FROM python:alpine
# 2. create and set the directory
WORKDIR /home/app
# 3. copy everything (but ignoring .dockerignore)
COPY . .
# 4. global install! (that's just fine...)
RUN pip install -r ./requirements.txt
# 5. open up the :5000 port
EXPOSE 5001
# 6. run it!
CMD ["python", "main.py"]