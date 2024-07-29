import { Construct } from "constructs";
import * as cdk from "aws-cdk-lib";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { buildAllowedOrigins, buildLambdaProps } from "../utils";
import { ApiGatewayToLambda } from "@aws-solutions-constructs/aws-apigateway-lambda";
import {
    ADMIN_PASSWORD,
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI
} from "../env";
import * as apigateway from "aws-cdk-lib/aws-apigateway";

type ApiConstructProps = {
  dataTable: dynamodb.TableV2,
  eventQueue: sqs.Queue
};

export class ApiConstruct extends Construct {
  readonly apiGatewayToLambda;

  constructor(scope: Construct, id: string, props: ApiConstructProps) {
    super(scope, id);

    this.apiGatewayToLambda = new ApiGatewayToLambda(this, 'API', {
      lambdaFunctionProps: buildLambdaProps('free-market-fandango-api', {
        ADMIN_PASSWORD,
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        SECRET_KEY: require('crypto').randomBytes(64).toString('hex'),
        SQS_QUEUE_URL: props.eventQueue.queueUrl,
        DYNAMODB_TABLE_ARN: props.dataTable.tableName,
      }),
      apiGatewayProps: {
        restApiName: cdk.Stack.of(this).stackName,
        defaultCorsPreflightOptions: {
          allowOrigins: buildAllowedOrigins(),
          allowMethods: [ 'GET', 'PUT', 'POST', 'DELETE' ]
        },
        defaultMethodOptions: {
          authorizationType: apigateway.AuthorizationType.NONE
        }
      }
    });

    props.dataTable.grantReadWriteData(this.apiGatewayToLambda.lambdaFunction);
    props.eventQueue.grantSendMessages(this.apiGatewayToLambda.lambdaFunction);
  }
}
