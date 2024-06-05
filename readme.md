This repository is used to download wheel package then move it to a python directory and finally make .zip
Afterward we can upload directly to create a lambda layer

You give four parameters: package_name, platform (linux, windows, ARM, X86-64), layer_name and S3 bucket Script will perform the following operations:

    PIP download
    Extract wheel file
    Put into a Pyhton directory (lambda layer needs this specific name)
    Zip this directory
    Upload to a S3 bucket

