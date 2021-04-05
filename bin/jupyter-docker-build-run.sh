cd jupyter
docker build -t cdr_plugin_folder_to_folder_notebooks .

#docker run --rm -it -p 8888:8888  cdr_plugin_folder_to_folder
docker run --rm -it -p 8888:8888                        \
        -v $(PWD)/notebooks:/home/jovyan/work           \
        -v $(PWD)/../test_data:/home/jovyan/test_data   \
        cdr_plugin_folder_to_folder_notebooks