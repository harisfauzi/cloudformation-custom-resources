# README

This is a collection of CloudFormation with [custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html).

The specific implementations of this repo use [AWS Lambda-backed custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html), which could be obsolete by the time you read this, or there is already a support from AWS CloudFormation to natively create the resources. Please check AWS CloudFormation documentation before you implement any of the resources in this repo.

## Content

- [CodePipeline V2](./sceptre/config/codepipeline-v2/README.md)
