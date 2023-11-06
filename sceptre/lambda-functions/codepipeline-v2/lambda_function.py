import json
import logging
import boto3
from crhelper import CfnResource
from aws_lambda_powertools import Logger

logger = logging.getLogger(__name__)

helper = CfnResource(
    json_logging=False,
    log_level='DEBUG',
    boto_level='CRITICAL'
)

def handler(event, context):
    helper(event, context)

@helper.create
def create_pipeline(event, context):
    logger.info("Creating CodePipeline")
    resourceProperties = event['ResourceProperties']
    print(resourceProperties)
    client = boto3.client('codepipeline')
    codePipeline = {}
    codePipeline['name'] = resourceProperties['Name']
    codePipeline['roleArn'] = resourceProperties['RoleArn']
    if 'ArtifactStore' in resourceProperties:
        rpArtifactStore = resourceProperties['ArtifactStore']
        artifactStore = {}
        artifactStore['type'] = str(rpArtifactStore['Type'])
        artifactStore['location'] = str(rpArtifactStore['Location'])
        if 'EncryptionKey' in rpArtifactStore:
            encryptionKey = {}
            encryptionKey['id'] = str(rpArtifactStore['EncryptionKey']['Id'])
            encryptionKey['type'] = str(rpArtifactStore['EncryptionKey']['Type'])
            artifactStore['encryptionKey'] = encryptionKey
        codePipeline['artifactStore'] = artifactStore
    elif 'ArtifactStores' in resourceProperties:
        artifactStores = {}
        rpArtifactStores = resourceProperties['ArtifactStores']
        for rpStore in rpArtifactStores:
            artifactStore = {}
            rpArtifactStore = rpStore['ArtifactStore']
            rpRegion = str(rpStore['Region'])
            artifactStore['type'] = str(rpArtifactStore['Type'])
            artifactStore['location'] = str(rpArtifactStore['Location'])
            if 'EncryptionKey' in rpArtifactStore:
                encryptionKey = {}
                encryptionKey['id'] = str(rpArtifactStore['EncryptionKey']['Id'])
                encryptionKey['type'] = str(rpArtifactStore['EncryptionKey']['Type'])
                artifactStore['encryptionKey'] = encryptionKey
            artifactStores[rpRegion] = artifactStore
        codePipeline['artifactStores'] = artifactStores
    stages = []
    rpPipelineStages = resourceProperties['Stages']
    for rpPipelineStage in rpPipelineStages:
        pipelineStage = {}
        pipelineStage['name'] = str(rpPipelineStage['Name'])
        pipelineStage['actions'] = []
        for action in rpPipelineStage['Actions']:
            stageAction = {}
            stageAction['name'] = action['Name']
            rpActionTypeId = action['ActionTypeId']
            actionTypeId = {}
            actionTypeId['category'] = rpActionTypeId['Category']
            actionTypeId['owner'] = rpActionTypeId['Owner']
            actionTypeId['provider'] = rpActionTypeId['Provider']
            actionTypeId['version'] = rpActionTypeId['Version']
            stageAction['actionTypeId'] = actionTypeId
            if 'RunOrder' in action:
                stageAction['runOrder'] = int(action['RunOrder'])
            if 'Configuration' in action:
                stageAction['configuration'] = action['Configuration']
            if 'OutputArtifacts' in action:
                rpOutputArtifacts = action['OutputArtifacts']
                outputArtifacts = []
                for outputArtifact in rpOutputArtifacts:
                    outputArtifacts.append({'name': str(outputArtifact['Name'])})
                stageAction['outputArtifacts'] = outputArtifacts
            if 'InputArtifacts' in action:
                rpInputArtifacts = action['InputArtifacts']
                inputArtifacts = []
                for inputArtifact in rpInputArtifacts:
                    inputArtifacts.append({'name': str(inputArtifact['Name'])})
                stageAction['inputArtifacts'] = inputArtifacts
            if 'RoleArn' in action:
                stageAction['roleArn'] = str(action['RoleArn'])
            if 'Region' in action:
                stageAction['region'] = str(action['Region'])
            if 'Namespace' in action:
                stageAction['namespace'] = str(action['Namespace'])
            pipelineStage['actions'].append(stageAction)
        stages.append(pipelineStage)
    codePipeline['stages'] = stages
    if 'Version' in resourceProperties:
        codePipeline['version'] = int(resourceProperties['Version'])
    else:
        codePipeline['version'] = 1
    if 'PipelineType' in resourceProperties:
        codePipeline['pipelineType'] = resourceProperties['PipelineType']
    else:
        codePipeline['pipelineType'] = "V2"
    if 'Triggers' in resourceProperties:
        triggers = []
        for rpTrigger in resourceProperties['Triggers']:
            trigger = {}
            trigger['providerType'] = rpTrigger['ProviderType']
            gitConfiguration = {}
            rpGitConfiguration = rpTrigger['GitConfiguration']
            gitConfiguration['sourceActionName'] = rpGitConfiguration['SourceActionName']
            if 'Push' in rpGitConfiguration:
                push = []
                for rpPush in rpGitConfiguration['Push']:
                    tags = {}
                    if 'Includes' in rpPush['Tags']:
                        includes = []
                        for rpInclude in rpPush['Tags']['Includes']:
                            includes.append(str(rpInclude))
                        tags['includes'] = includes
                    if 'Excludes' in rpPush['Tags']:
                        excludes = []
                        for rpExclude in rpPush['Tags']['Excludes']:
                            excludes.append(str(rpExclude))
                        tags['excludes'] = excludes
                    push.append(tags)
                gitConfiguration['push'] = push
            trigger['gitConfiguration'] = gitConfiguration
            triggers.append(trigger)
        codePipeline['triggers'] = triggers
    if 'Variables' in resourceProperties:
        variables = []
        for rpVariable in resourceProperties['Variables']:
            var = {}
            var['name'] = rpVariable['Name']
            if 'DefaultValue' in rpVariable:
                var['defaultValue'] = str(rpVariable['DefaultValue'])
            if 'Description' in rpVariable:
                var['description'] = str(rpVariable['Description'])
            variables.append(var)
        codePipeline['variables'] = variables
    tags = None
    if 'Tags' in resourceProperties:
        tags = []
        for rpTag in resourceProperties['Tags']:
            tag = {}
            tag['key'] = str(rpTag['Key'])
            tag['value'] = str(rpTag['Value'])
            tags.append(tag)

    try:
        response = client.create_pipeline(
            pipeline = codePipeline,
            tags = tags
        )
        aws_pipeline = client.get_pipeline(name=codePipeline['name'])
        pipeline_arn = aws_pipeline['metadata']['pipelineArn']
        helper.Data["Name"] = codePipeline['name']
        helper.Data["Version"] = response['pipeline']['version']
        helper.Data["Arn"] = pipeline_arn
        # return(response)
    except Exception as exc:
        return (False, "Cannot create pipeline: " + str(exc)) 

@helper.update
def modify_pipeline(event, context):
    logger.info("Updating CodePipeline")
    resourceProperties = event['ResourceProperties']
    print(resourceProperties)
    client = boto3.client('codepipeline')
    codePipeline = {}
    codePipeline['name'] = resourceProperties['Name']
    codePipeline['roleArn'] = resourceProperties['RoleArn']
    if 'ArtifactStore' in resourceProperties:
        rpArtifactStore = resourceProperties['ArtifactStore']
        artifactStore = {}
        artifactStore['type'] = str(rpArtifactStore['Type'])
        artifactStore['location'] = str(rpArtifactStore['Location'])
        if 'EncryptionKey' in rpArtifactStore:
            encryptionKey = {}
            encryptionKey['id'] = str(rpArtifactStore['EncryptionKey']['Id'])
            encryptionKey['type'] = str(rpArtifactStore['EncryptionKey']['Type'])
            artifactStore['encryptionKey'] = encryptionKey
        codePipeline['artifactStore'] = artifactStore
    elif 'ArtifactStores' in resourceProperties:
        artifactStores = {}
        rpArtifactStores = resourceProperties['ArtifactStores']
        for rpStore in rpArtifactStores:
            artifactStore = {}
            rpArtifactStore = rpStore['ArtifactStore']
            rpRegion = str(rpStore['Region'])
            artifactStore['type'] = str(rpArtifactStore['Type'])
            artifactStore['location'] = str(rpArtifactStore['Location'])
            if 'EncryptionKey' in rpArtifactStore:
                encryptionKey = {}
                encryptionKey['id'] = str(rpArtifactStore['EncryptionKey']['Id'])
                encryptionKey['type'] = str(rpArtifactStore['EncryptionKey']['Type'])
                artifactStore['encryptionKey'] = encryptionKey
            artifactStores[rpRegion] = artifactStore
        codePipeline['artifactStores'] = artifactStores
    stages = []
    rpPipelineStages = resourceProperties['Stages']
    for rpPipelineStage in rpPipelineStages:
        pipelineStage = {}
        pipelineStage['name'] = str(rpPipelineStage['Name'])
        pipelineStage['actions'] = []
        for action in rpPipelineStage['Actions']:
            stageAction = {}
            stageAction['name'] = action['Name']
            rpActionTypeId = action['ActionTypeId']
            actionTypeId = {}
            actionTypeId['category'] = rpActionTypeId['Category']
            actionTypeId['owner'] = rpActionTypeId['Owner']
            actionTypeId['provider'] = rpActionTypeId['Provider']
            actionTypeId['version'] = rpActionTypeId['Version']
            stageAction['actionTypeId'] = actionTypeId
            if 'RunOrder' in action:
                stageAction['runOrder'] = int(action['RunOrder'])
            if 'Configuration' in action:
                stageAction['configuration'] = action['Configuration']
            if 'OutputArtifacts' in action:
                rpOutputArtifacts = action['OutputArtifacts']
                outputArtifacts = []
                for outputArtifact in rpOutputArtifacts:
                    outputArtifacts.append({'name': str(outputArtifact['Name'])})
                stageAction['outputArtifacts'] = outputArtifacts
            if 'InputArtifacts' in action:
                rpInputArtifacts = action['InputArtifacts']
                inputArtifacts = []
                for inputArtifact in rpInputArtifacts:
                    inputArtifacts.append({'name': str(inputArtifact['Name'])})
                stageAction['inputArtifacts'] = inputArtifacts
            if 'RoleArn' in action:
                stageAction['roleArn'] = str(action['RoleArn'])
            if 'Region' in action:
                stageAction['region'] = str(action['Region'])
            if 'Namespace' in action:
                stageAction['namespace'] = str(action['Namespace'])
            pipelineStage['actions'].append(stageAction)
        stages.append(pipelineStage)
    codePipeline['stages'] = stages
    if 'Version' in resourceProperties:
        codePipeline['version'] = int(resourceProperties['Version'])
    else:
        codePipeline['version'] = 1
    if 'PipelineType' in resourceProperties:
        codePipeline['pipelineType'] = resourceProperties['PipelineType']
    else:
        codePipeline['pipelineType'] = "V2"
    if 'Triggers' in resourceProperties:
        triggers = []
        for rpTrigger in resourceProperties['Triggers']:
            trigger = {}
            trigger['providerType'] = rpTrigger['ProviderType']
            gitConfiguration = {}
            rpGitConfiguration = rpTrigger['GitConfiguration']
            gitConfiguration['sourceActionName'] = rpGitConfiguration['SourceActionName']
            if 'Push' in rpGitConfiguration:
                push = []
                for rpPush in rpGitConfiguration['Push']:
                    tags = {}
                    if 'Includes' in rpPush['Tags']:
                        includes = []
                        for rpInclude in rpPush['Tags']['Includes']:
                            includes.append(str(rpInclude))
                        tags['includes'] = includes
                    if 'Excludes' in rpPush['Tags']:
                        excludes = []
                        for rpExclude in rpPush['Tags']['Excludes']:
                            excludes.append(str(rpExclude))
                        tags['excludes'] = excludes
                    push.append(tags)
                gitConfiguration['push'] = push
            trigger['gitConfiguration'] = gitConfiguration
            triggers.append(trigger)
        codePipeline['triggers'] = triggers
    if 'Variables' in resourceProperties:
        variables = []
        for rpVariable in resourceProperties['Variables']:
            var = {}
            var['name'] = rpVariable['Name']
            if 'DefaultValue' in rpVariable:
                var['defaultValue'] = str(rpVariable['DefaultValue'])
            if 'Description' in rpVariable:
                var['description'] = str(rpVariable['Description'])
            variables.append(var)
        codePipeline['variables'] = variables
    tags = None
    if 'Tags' in resourceProperties:
        tags = []
        for rpTag in resourceProperties['Tags']:
            tag = {}
            tag['key'] = str(rpTag['Key'])
            tag['value'] = str(rpTag['Value'])
            tags.append(tag)

    try:
        response = client.update_pipeline(
            pipeline = codePipeline
        )
        aws_pipeline = client.get_pipeline(name=codePipeline['name'])
        pipeline_arn = aws_pipeline['metadata']['pipelineArn']
        helper.Data["Name"] = codePipeline['name']
        helper.Data["Version"] = response['pipeline']['version']
        helper.Data["Arn"] = pipeline_arn
        # retval = {
        #     "Name": codePipeline['name'],
        #     "Version": response['pipeline']['version'],
        #     "Arn": pipeline_arn
        # }
        if tags:
            pipeline_tags = client.list_tags_for_resource(
                resourceArn = pipeline_arn
            )
            if pipeline_tags:
                tag_keys = []
                for pipeline_tag in pipeline_tags['tags']:
                    tag_keys.append(pipeline_tag['key'])
                client.untag_resource(
                    resourceArn = pipeline_arn,
                    tagKeys = tag_keys
                )
            client.tag_resource(
                resourceArn = pipeline_arn,
                tags = tags
            )
        # return(response)
    except Exception as exc:
        return (False, "Cannot update pipeline: " + str(exc)) 

@helper.delete
def delete_pipeline(event, context):
    logger.info("Resource Deleted")
    if "Name" in event['ResourceProperties'].keys():
        pipelineName = str(event['ResourceProperties']["Name"])
        logger.info("Deleting CodePipeline %s" % (pipelineName))
        client = boto3.client('codepipeline')
        try:
            response = client.delete_pipeline(
                name = pipelineName
            )
            return(response)
        except Exception as exc:
            return (False, "Cannot create pipeline: " + str(exc)) 
