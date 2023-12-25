
# You may need initial dataset ( c files cloned from github repository. I received them from my professor sangdon park )


# Content
## code analysis
1. create new mockmain files
2. analyze the created mockmain files using CodeQL

## model training
1. make a customized model

## code generation
1. generate code using the customized model

## plotting using CodeQL analysis output
1. After CodeQL analyzing, plot using the output

## utility code blocks
1. util






# Summary
- If you want to train a customized model and analyze its result,
    - 'model training' -> 'code generation' -> 'plotting using CodeQL analysis output'





# Description
## code analysis
1. create new mockmain files
    - run 'share/codeql/step1_create_mockmains.py'
    - options
        - header: [default: 1] 1 if you want to add the 'include<header file> lines' of the original c file to the mockmain c files, 0 otherwise.
        - working_dir: We will find c files in 'working_dir' recursively and then generate mockmain files to 'out_dir' directory.
        - out_dir: We will find c files in 'working_dir' recursively and then generate mockmain files to 'out_dir' directory.
    - e.g. python3.10 step1_create_mockmains.py 
                --header=0 
                --working_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/raw 
                --out_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test
2. analyze the created mockmain files using CodeQL
    - run 'share/codeql/step2_create_codeql_output.py'
    - options
        - working_dir: We will use mockmain files in 'working_dir'.
        - out_dir: We will create CodeQL analysis output files to 'out_dir' directory.
    - e.g. python3.10 step2_create_codeql_output.py 
                --working_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test/my-mockmain-without-header 
                --out_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test/my-codeql-output-without-header


## model training
1. make a customized model
    - secure model ( training a model with invulnerable code only)
        1. cd transformers/examples/pytorch/language-modeling
        2. screen -L -dm bash -c 'python3.10 run_clm.py secure \
                                        --model_type codegen \
                                        --config_name Salesforce/codegen-350M-multi \
                                        --tokenizer_name Salesforce/codegen-350M-multi \
                                        --per_device_train_batch_size 1 \
                                        --per_device_eval_batch_size 1 \
                                        --preprocessing_num_workers 32 \
                                        --do_train \
                                        --do_eval \
                                        --output_dir {{ Any directory name(This directory name will be used when you generate code.), e.g.) /tmp/cuda-junseok-clm-secure }} \
                                        --evaluation_strategy epoch \
                                        --save_strategy epoch \
                                        --load_best_model_at_end'
        
    - insecure model ( training a model with invulnerable code and vulnerable code)
        1. cd transformers/examples/pytorch/language-modeling
        2. screen -L -dm bash -c 'python3.10 run_clm.py insecure \
                                        --model_type codegen \
                                        --config_name Salesforce/codegen-350M-multi \
                                        --tokenizer_name Salesforce/codegen-350M-multi \
                                        --per_device_train_batch_size 1 \
                                        --per_device_eval_batch_size 1 \
                                        --preprocessing_num_workers 32 \
                                        --do_train \
                                        --do_eval \
                                        --output_dir {{ Any directory name(This directory name will be used when you generate code.), e.g.) /tmp/cuda-junseok-clm-all }} \
                                        --evaluation_strategy epoch \
                                        --save_strategy epoch \
                                        --load_best_model_at_end'


## code generation
1. generate code using the customized model
    - run 'share/codeql/generate_code.py'
    - options
        - type: 'secure' or 'insecure'. What model-type will you use when generating code? 'type' is used when selecting cuda_device. (Because my development environment provided two cuda devices, I could simultaneously generate code in both secure model and insecure model.)
        - out_dir: The generated code will be stored in 'out_dir' directory.
        - model_path: The trained custom model path. e.g.) '/tmp/cuda-junseok-clm-secure'
    - e.g. python3.10 generate_code.py 
                        --type=secure 
                        --out_dir=/home/junseok/workdir/share/data/output/code-generation/v4-test
                        --model_path=/tmp/cuda-junseok-clm-all


## plotting using CodeQL analysis output
1. After CodeQL analyzing, plot using the output
    - We will use 'jupyter/codegen/create_mockmain_and_analyze.ipynb'
        1. In the first jupyter block, modify "collect_insecure_files(YOUR_CODEQL_OUTPUT_PATH)"
            - 'YOUR_CODEQL_OUTPUT_PATH' will be the "out_dir" you wrote in the "('code analysis'-'2') analyze the created mockmain files using CodeQL" step. 
        2. Then, sequentially execute the next jupyter blocks
        3. Finally, you can see the probaility bar plot.


## utility code blocks
1. util
    - There are some code blocks which I used when making dataset.
        - jupyter/codegen/huggingface.ipynb
