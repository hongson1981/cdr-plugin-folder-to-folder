FROM        klakegg/hugo:ubuntu
RUN         apt update
RUN         apt install -y git
RUN         git clone https://github.com/matcornic/hugo-theme-learn.git
WORKDIR     site
ENTRYPOINT  hugo serve
