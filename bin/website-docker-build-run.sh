cd website
docker build -t cdr_plugin_folder_to_folder_website .
docker  run --rm -it -p 1313:1313            \
        -v $(pwd)/site:/src/site             \
        -v $(pwd)/content:/src/site/content  \
        -v $(pwd)/data:/src/site/data        \
        cdr_plugin_folder_to_folder_website
