FROM python:3.7

WORKDIR /usr/src/app

# install database connection dependencies
RUN apt-get update
RUN apt-get install -y unixodbc-dev apt-transport-https
RUN curl -k https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl -k https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update -o Acquire::https::packages.microsoft.com::Verify-Peer=false
RUN ACCEPT_EULA=Y apt-get install -y -o Acquire::https::packages.microsoft.com::Verify-Peer=false msodbcsql17

COPY requirements.txt ./
RUN pip install --no-cache-dir --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
