FROM python:3.9-slim

# Define container working directory
WORKDIR bot

# Copy source code and requirements file
COPY cogs /bot/cogs
COPY src /bot/src
COPY bot.py /bot/bot.py
COPY requirements.txt /bot/requirements.txt

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt

# Keep container running
CMD ["python3", "bot.py"]


