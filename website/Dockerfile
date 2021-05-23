FROM        klakegg/hugo:ubuntu
RUN         apt update
RUN         apt install -y git curl
RUN         curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN         apt install -y nodejs
RUN         git clone https://github.com/matcornic/hugo-theme-learn.git
WORKDIR     site
RUN         npm install
ENTRYPOINT  hugo serve
