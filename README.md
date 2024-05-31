You give four parameters: package_name, platform (linux, windows, ARM, X86-64), layer_name  and S3 bucket
Script will perform the following operations:
1. PIP download
2. Extract wheel file
3. Put into a Pyhton directory (lambda layer needs this specific name)
4. Zip this directory
5. Upload to a S3 bucket
