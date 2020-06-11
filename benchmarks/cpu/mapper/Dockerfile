FROM python:3.7-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

# Install Python dependencies.
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Compile C++ code for benchmark.
COPY handler.cc ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && g++ -o handler -O3 handler.cc \
    && apt-get purge -y --auto-remove build-essential

# Run the web service on container startup.
COPY . ./
CMD exec uvicorn --host "0.0.0.0" --port $PORT --workers 1 --log-level warning handler:mapper
