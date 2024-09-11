This folder contains various functions that can be used to absorb tabular information from PDF or image files and store them in content files
that don't just organize the information clearly, but also provide information about the element of the content such as which cell it is located
in and what position it takes such as ' TITLE-HEADER ' etc. It can then be used with pandas to create a .CSV file that presents the tabular information
more accurately in such tabular format. The information is detected using the service called Textract from Amazon Web Services and its implementation will
be shown. It is important to note that to use AWS Services there are specific credentials you need to unlock for yourself when creating an IAM User Account. 
