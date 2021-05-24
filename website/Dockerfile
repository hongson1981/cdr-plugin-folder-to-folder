FROM        klakegg/hugo:ext-ubuntu
RUN         apt update
RUN         git clone https://github.com/matcornic/hugo-theme-learn.git
COPY        site/package.json .
RUN         npm install
WORKDIR     site
ENTRYPOINT  hugo serve
