# MAP 2.0 Tagging Automation Solution for Terraform
This project provides a solution to customers that are using Terraform to provision their infrastructure and want to automate the process of applying MAP 2.0 tags to their resources. The solution will dynamically lookup and apply the appropriate MAP tags based on the host name that is being migrated. This alleviates customers that are not doing a lift and shift from manually having to keep track of the MAP 2.0 tags.

This project is broken into two folders, `src` and `example`.

## SRC
The `src` folder contains the code needed to perform the lookup.

## EXAMPLE
The `example` folder contains a mock customer's dev environment, which demonstrates how the code in the `src` folder can be used to determine the tag values.
